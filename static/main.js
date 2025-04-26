document.addEventListener('DOMContentLoaded', () => {

    const heroImages = [
        'hero-images/hero1.png',
        'hero-images/hero2.png',
        'hero-images/hero3.png',
        'hero-images/hero4.png'
    ];

    const randomIndex = Math.floor(Math.random() * heroImages.length);
    const randomImage = heroImages[randomIndex];

    const heroImageEl = document.getElementById('heroImage');
    if (heroImageEl) {
        heroImageEl.src = randomImage;
    }
});