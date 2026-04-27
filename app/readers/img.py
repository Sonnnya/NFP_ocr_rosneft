import asyncio
from pathlib import Path

from parsing_app.integrations.suria_ocr import get_ocr_from_file, parse_result

from .readers import ABCBillReader, ReadersFactory


def img_to_txt(filepath: str) -> str:
    return parse_result(get_ocr_from_file(filepath))


@ReadersFactory.register_reader(".jpg")
@ReadersFactory.register_reader(".png")
class IMGReader(ABCBillReader):
    async def get_requisitions(self, filepath: str) -> str:
        print(f"Got file: {filepath}")
        return await asyncio.to_thread(img_to_txt, filepath)


if __name__ == "__main__":
    path = Path(
        r".\data\Единый ЦУПИС\ИИ для создания заявки\виды_формы\3352_Есакова Светлана Сергеевна (самозанятый)_Pe7_8 400,00 (RUB)_акт флориста.jpg"
    )

    async def main():
        print(await IMGReader().get_requisitions(path.as_posix()))

    asyncio.run(main())
