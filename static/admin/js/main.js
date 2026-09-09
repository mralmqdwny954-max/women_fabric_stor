// ضغط الصور قبل رفعها من لوحة التحكم

document.querySelectorAll('input[type="file"][accept*="image"]').forEach(input => {

    input.addEventListener("change", async function () {

        const file = this.files[0];

        if (!file) return;

        // إذا كانت الصورة صغيرة أصلًا، لا نضغطها
        if (file.size <= 1200 * 1024) {
            return;
        }

        const image = new Image();

        image.src = URL.createObjectURL(file);

        await new Promise(resolve => {
            image.onload = resolve;
        });

        const maxWidth = 1600;
        const maxHeight = 1600;

        let width = image.width;
        let height = image.height;

        if (width > maxWidth || height > maxHeight) {

            const ratio = Math.min(
                maxWidth / width,
                maxHeight / height
            );

            width = Math.round(width * ratio);
            height = Math.round(height * ratio);
        }

        const canvas = document.createElement("canvas");

        canvas.width = width;
        canvas.height = height;

        const ctx = canvas.getContext("2d");

        ctx.drawImage(
            image,
            0,
            0,
            width,
            height
        );

        const blob = await new Promise(resolve => {
            canvas.toBlob(
                resolve,
                "image/jpeg",
                0.82
            );
        });

        URL.revokeObjectURL(image.src);

        if (!blob) return;

        const compressedFile = new File(
            [blob],
            file.name.replace(/\.[^/.]+$/, "") + ".jpg",
            {
                type: "image/jpeg",
                lastModified: Date.now()
            }
        );

        const dataTransfer = new DataTransfer();

        dataTransfer.items.add(compressedFile);

        this.files = dataTransfer.files;

    });

});