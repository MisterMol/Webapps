document.addEventListener("DOMContentLoaded", function () {
    const lightbox = document.getElementById("imageLightbox");

    if (!lightbox) {
        return;
    }

    const image = lightbox.querySelector(".image-lightbox-img");
    const closeButton = lightbox.querySelector(".image-lightbox-close");
    const triggers = document.querySelectorAll("[data-lightbox-src]");

    function openLightbox(src, alt) {
        image.src = src;
        image.alt = alt || "";
        lightbox.classList.add("is-open");
        lightbox.setAttribute("aria-hidden", "false");
        document.body.classList.add("lightbox-open");
    }

    function closeLightbox() {
        lightbox.classList.remove("is-open");
        lightbox.setAttribute("aria-hidden", "true");
        document.body.classList.remove("lightbox-open");

        window.setTimeout(function () {
            if (!lightbox.classList.contains("is-open")) {
                image.src = "";
                image.alt = "";
            }
        }, 180);
    }

    triggers.forEach(function (trigger) {
        trigger.addEventListener("click", function () {
            openLightbox(trigger.dataset.lightboxSrc, trigger.dataset.lightboxAlt);
        });
    });

    closeButton.addEventListener("click", closeLightbox);

    lightbox.addEventListener("click", function (event) {
        if (event.target === lightbox || event.target.classList.contains("image-lightbox-inner")) {
            closeLightbox();
        }
    });

    document.addEventListener("keydown", function (event) {
        if (event.key === "Escape" && lightbox.classList.contains("is-open")) {
            closeLightbox();
        }
    });
});
