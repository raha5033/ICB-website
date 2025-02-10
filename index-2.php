<style>
    /* General image resizing */
    .resized-image {
        width: 100%;
        max-width: 400px;
        height: 260px;
        object-fit: cover;
    }

    /* Opening hours section images */
    .opening-time img {
        width: 100%;
        height: 160px;
        object-fit: cover;
    }

    /* Blog section images */
    .blog-two figure img {
        width: 100%;
        height: 260px;
        object-fit: cover;
    }

    /* Gallery images */
    .image-gallery img {
        width: 100%;
        height: 160px;
        object-fit: cover;
    }

    /* Hero section image */
    .hero-img img {
        width: 100%;
        max-width: 600px;
        height: auto;
        object-fit: cover;
    }

    /* Responsive adjustments */
    @media (max-width: 768px) {
        .resized-image,
        .blog-two figure img {
            height: 200px;
        }
        
        .opening-time img,
        .image-gallery img {
            height: 140px;
        }
    }

    @media (max-width: 576px) {
        .resized-image,
        .blog-two figure img {
            height: 180px;
        }
        
        .opening-time img,
        .image-gallery img {
            height: 120px;
        }
    }
</style> 