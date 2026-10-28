import io
import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter

class ImageEnhancer:
    """
    Xira (blurry), past sifatli rasmlarni tahlil qilish, shovqinni tozalash,
    kontrastni yaxshilash va tiniqlashtirish (enhancement / upscaling) moduli.
    """

    @staticmethod
    def _bytes_to_cv2(image_bytes: bytes) -> np.ndarray:
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError("Rasmni o'qib bo'lmadi.")
        return img

    @staticmethod
    def _cv2_to_bytes(img: np.ndarray, ext: str = ".jpg", quality: int = 95) -> bytes:
        if ext.lower() in [".jpg", ".jpeg"]:
            params = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
        elif ext.lower() == ".png":
            params = [int(cv2.IMWRITE_PNG_COMPRESSION), 4]
        else:
            params = []
        success, encoded_img = cv2.imencode(ext, img, params)
        if not success:
            raise ValueError("Rasmni kodlashda xatolik yuz berdi.")
        return encoded_img.tobytes()

    @classmethod
    def enhance_auto_hd(cls, image_bytes: bytes, scale: float = 2.0) -> bytes:
        """
        Asosiy Ultra HD yaxshilash:
        1. Shovqinni kamaytirish (Denoising / Bilateral filter)
        2. Kengaytirish (Lanczos Super-Resolution Upscaling)
        3. LAB rang fazosida yorug'lik va kontrastni adaptiv oshirish (CLAHE)
        4. Nozik detallarni kuchaytirish (Unsharp Masking)
        5. Rang to'yinganligini muvozanatlash
        """
        img = cls._bytes_to_cv2(image_bytes)
        h, w = img.shape[:2]

        # 1. Bilateral filtr - qirralarni saqlagan holda xiralik va shovqinni yo'qotadi
        denoised = cv2.bilateralFilter(img, d=7, sigmaColor=50, sigmaSpace=50)

        # 2. Yuqori sifatli Lanczos4 interpolyatsiyasi orqali masshtabni kattalashtirish
        new_w = int(w * scale)
        new_h = int(h * scale)
        upscaled = cv2.resize(denoised, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)

        # 3. CLAHE (Contrast Limited Adaptive Histogram Equalization) - LAB rang maydonida
        lab = cv2.cvtColor(upscaled, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.2, tileGridSize=(8, 8))
        l_enhanced = clahe.apply(l)
        lab_enhanced = cv2.merge((l_enhanced, a, b))
        contrast_boosted = cv2.cvtColor(lab_enhanced, cv2.COLOR_LAB2BGR)

        # 4. Unsharp Masking (Qirralarni keskinlashtirish va tiniqlashtirish)
        gaussian_blur = cv2.GaussianBlur(contrast_boosted, (0, 0), sigmaX=2.0)
        sharpened = cv2.addWeighted(contrast_boosted, 1.5, gaussian_blur, -0.5, 0)

        # 5. Detail enhance (detallarni bo'rttirib ko'rsatish)
        try:
            detailed = cv2.detailEnhance(sharpened, sigma_s=10, sigma_r=0.15)
        except Exception:
            detailed = sharpened

        # Yakuniy natijani qaytarish
        return cls._cv2_to_bytes(detailed, ext=".jpg", quality=96)

    @classmethod
    def enhance_portrait(cls, image_bytes: bytes) -> bytes:
        """
        Portret va yuzlar uchun maxsus rejim:
        Teri silliqligi va ko'z/qosh/soch qirralarini aniqlashtirish
        """
        img = cls._bytes_to_cv2(image_bytes)
        h, w = img.shape[:2]

        # Yuz terisidagi mayda xiralik va shovqinni yumshatish
        smooth = cv2.bilateralFilter(img, d=9, sigmaColor=75, sigmaSpace=75)

        # 2x kattalashtirish
        upscaled = cv2.resize(smooth, (int(w * 2), int(h * 2)), interpolation=cv2.INTER_CUBIC)

        # LAB orqali yumshoq kontrast
        lab = cv2.cvtColor(upscaled, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=1.6, tileGridSize=(8, 8))
        l_enhanced = clahe.apply(l)
        enhanced_bgr = cv2.cvtColor(cv2.merge((l_enhanced, a, b)), cv2.COLOR_LAB2BGR)

        # Qirralarni keskinlashtirish (Unsharp mask)
        blur = cv2.GaussianBlur(enhanced_bgr, (0, 0), 1.5)
        result = cv2.addWeighted(enhanced_bgr, 1.35, blur, -0.35, 0)

        return cls._cv2_to_bytes(result, ext=".jpg", quality=96)

    @classmethod
    def enhance_super_res_4x(cls, image_bytes: bytes) -> bytes:
        """
        4x o'lchamga kattalashtirish va chuqur qirra tiklash
        """
        img = cls._bytes_to_cv2(image_bytes)
        h, w = img.shape[:2]

        # Juda katta rasmlar xotirani to'ldirib yubormasligi uchun tekshirish
        if w * h > 2500 * 2500:
            scale = 2.0
        else:
            scale = 4.0

        target_w = int(w * scale)
        target_h = int(h * scale)

        # Denoise
        denoised = cv2.bilateralFilter(img, d=5, sigmaColor=40, sigmaSpace=40)

        # Lanczos4 kattalashtirish
        upscaled = cv2.resize(denoised, (target_w, target_h), interpolation=cv2.INTER_LANCZOS4)

        # CLAHE
        lab = cv2.cvtColor(upscaled, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
        l_enhanced = clahe.apply(l)
        enhanced_bgr = cv2.cvtColor(cv2.merge((l_enhanced, a, b)), cv2.COLOR_LAB2BGR)

        # Unsharp mask
        blur = cv2.GaussianBlur(enhanced_bgr, (0, 0), 2.5)
        sharpened = cv2.addWeighted(enhanced_bgr, 1.6, blur, -0.6, 0)

        return cls._cv2_to_bytes(sharpened, ext=".jpg", quality=95)

    @classmethod
    def enhance_fast(cls, image_bytes: bytes) -> bytes:
        """
        Tezkor tiklash (Kichik hajmli va tez natija)
        """
        img = cls._bytes_to_cv2(image_bytes)
        h, w = img.shape[:2]

        # 1.5x kattalashtirish
        upscaled = cv2.resize(img, (int(w * 1.5), int(h * 1.5)), interpolation=cv2.INTER_LANCZOS4)

        # Qirralarni kuchaytirish
        gaussian = cv2.GaussianBlur(upscaled, (0, 0), 2.0)
        sharpened = cv2.addWeighted(upscaled, 1.4, gaussian, -0.4, 0)

        return cls._cv2_to_bytes(sharpened, ext=".jpg", quality=92)
