from transformers import AutoModelForCausalLM, AutoTokenizer

model_name = "Qwen/Qwen3-0.6B"

# load the tokenizer and the model
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name, torch_dtype="auto", device_map="auto"
)

print(model.dtype, model.device)

# prepare the model input
prompt = """
описание рабочего процесса:

Основной запрос касается возможности автоматизированной проверки и формирования авансового отчета по командировкам.
В идеальном сценарии хотелось бы минимизировать участие бухгалтера в данном процессе ввиду значительного объема командировок и сопутствующей первичной документации.
 
Сейчас процесс выглядит следующим образом:
- сотрудник съездил в командировку, готовит авансовый отчет и прикладывает все подтверждающие документы
- пакет документов в виде сканов приходит в ОЦО
- бухгалтер ОЦО проверяет пакет на наличие необходимых документов, соответствие дат и сумм в комплекте, наличие подписей
- далее формирует проводки в учетной системе соответствующего Общества
 
Задачи требующие автоматизации:
- определить вид документа и к каждому документу в пакете подобрать атрибутивный состав и провести минимальные проверки (наличие подписей)
- проверить соответствие документов в пакете, строка в авансовом отчете соответствует приложенному документу
- после всех проверок собрать атрибуты в машиночитаемом виде и передать в учетную систему для отражения в учете

Я дам тебе данные билетов и АО, тебе нужно их сверить и ответить, можно ли провести авансовый отчет.

Данные билетов:
<doc>
{"input_doc_name": "Проезд",
"input_doc_number": "0650",
"input_doc_date": "29.05.2025",
"sum_main": 2535.50,
"sum_currency": 2535.50,
"account": "44",
"currency": "RUB"}
</doc>

Данные АО:
<doc>
[{"number": "124", 
"date": "01.06.2026",
"company": "ООО Метеор",
"accountable_person": "И.Н. Белов",
"branch": "",
"director": "К. М. Орлов",
"chief_accountant": "Г.Л.Ларина",
"accountant": "М.П. Куркина",
"currency": "RUB",
"comment": "", 
"expenses":
[{"input_doc_name": "суточные",
"input_doc_number": "237-09",
"input_doc_date": "25.05.2025",
"sum_main": 3000.00,
"sum_currency": 3000.00,
"account": "44",
"currency": "RUB"},
{"input_doc_name": "Проезд",
"input_doc_number": "0650",
"input_doc_date": "29.05.2025",
"sum_main": 2535.50,
"sum_currency": 2535.50,
"account": "44",
"currency": "RUB"},
{"input_doc_name": "Проживание",
"input_doc_number": "237-09",
"input_doc_date": "29.05.2025",
"sum_main": 28.00,
"sum_currency": 28.00,
"account": "44",
"currency": "RUB"}]
}]
</doc>

"""
messages = [{"role": "user", "content": prompt}]
text = tokenizer.apply_chat_template(
    messages,
    tokenize=False,
    add_generation_prompt=True,
    enable_thinking=False,  # Switches between thinking and non-thinking modes. Default is True.
)
model_inputs = tokenizer([text], return_tensors="pt").to(model.device)

# conduct text completion
generated_ids = model.generate(**model_inputs, max_new_tokens=32768)
output_ids = generated_ids[0][len(model_inputs.input_ids[0]) :].tolist()

# parsing thinking content
try:
    # rindex finding 151668 (</think>)
    index = len(output_ids) - output_ids[::-1].index(151668)
except ValueError:
    index = 0

thinking_content = tokenizer.decode(output_ids[:index], skip_special_tokens=True).strip(
    "\n"
)
content = tokenizer.decode(output_ids[index:], skip_special_tokens=True).strip("\n")

print("thinking content:", thinking_content)
print("content:", content)
