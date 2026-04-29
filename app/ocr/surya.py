import logging
from pathlib import Path

from PIL import Image
from surya.detection import DetectionPredictor
from surya.foundation import FoundationPredictor
from surya.recognition import RecognitionPredictor
from surya.recognition.schema import OCRResult

from app.settings import log_blob

logger = logging.getLogger(__name__)

foundation_predictor = FoundationPredictor()
recognition_predictor = RecognitionPredictor(foundation_predictor)
detection_predictor = DetectionPredictor()


def ocr_surya(img_objs: list[Image.Image]) -> list[OCRResult]:
    logger.debug(f"Running OCR on {len(img_objs)} images...")
    # NOTE: 1 за раз
    predictions = recognition_predictor(
        images=img_objs, det_predictor=detection_predictor
    )
    return predictions


def get_img_ocr(img_path: str) -> OCRResult:
    # imgs = [Image.open(img_path) for img_path in img_paths]
    img = [Image.open(img_path)]
    res = ocr_surya(img)
    res = res[0]
    return res


def parse_result(res: OCRResult) -> str:
    return "\n".join(line.text for line in res.text_lines)


def parse_results(ress: list[OCRResult]) -> list[str]:
    return [parse_result(res) for res in ress]


def ocr_and_log(img_objs: list[Image.Image], filenames: list[str]) -> list[str]:
    """
    OCR a batch and log each result with its filename as the label.
    Use this instead of calling ocr_surya + parse_result separately
    when you want per-file logging.
    """
    results = ocr_surya(img_objs)
    texts = []
    for res, name in zip(results, filenames):
        text = parse_result(res)
        log_blob(logger, f"OCR result: {name}", text)
        texts.append(text)
    return texts


if __name__ == "__main__":
    # path = "./data/examples/АО_билет/Образец АО.jpg"
    # _res = get_img_ocr("./data/examples/АО_билет/ЖД билет.png")
    # res = parse_result(_res)

    # print(_res)
    # print(res)

    dir = "./data/Образцы документов авансовый отчет"
    for img in Path(dir).rglob("*"):
        if img.suffix.lower() not in [".jpg", ".jpeg", ".png"]:
            continue

        print(img)
        _res = get_img_ocr(str(img))
        res = parse_result(_res)
        print(res)

        if img.with_suffix(".txt").exists():
            print(f"{img.with_suffix('.txt')} already exists, skipping")
            continue
        else:
            with open(img.with_suffix(".txt"), "w", encoding="utf-8") as f:
                f.write(res)
