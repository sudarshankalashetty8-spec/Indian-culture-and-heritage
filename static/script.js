const container = document.getElementById('content-area');
const searchInput = document.getElementById('search');
const searchBtn = document.getElementById('search-btn');
const tabButtons = document.querySelectorAll('.tab-btn');
const modal = document.getElementById('detail-modal');
const closeBtn = document.querySelector('.close-btn');
const totalItemsEl = document.getElementById('total-items');

const FALLBACK_IMAGES = {
    festivals:      'https://images.unsplash.com/photo-1574015974293-817f0ebebb74?w=400&h=300&fit=crop',
    dance_forms:    'https://images.unsplash.com/photo-1545959570-a94084071b5d?w=400&h=300&fit=crop',
    heritage_sites: 'https://images.unsplash.com/photo-1548013146-72479768bada?w=400&h=300&fit=crop',
    cuisine:        'https://images.unsplash.com/photo-1585937421612-70a008356fbe?w=400&h=300&fit=crop',
    music:          'https://images.unsplash.com/photo-1511192336575-5a79af67a629?w=400&h=300&fit=crop',
    art_forms:      'https://images.unsplash.com/photo-1579783902614-a3fb3927b6a5?w=400&h=300&fit=crop',
    languages:      'https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?w=400&h=300&fit=crop'
};
const DEFAULT_FALLBACK = 'https://images.unsplash.com/photo-1524492412937-b28074a5d7da?w=400&h=300&fit=crop';

let allData = [];
let currentCategory = 'all';

function getFallback(category) {
    return FALLBACK_IMAGES[category] || DEFAULT_FALLBACK;
}

function formatCategory(category) {
    return category.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
}

async function fetchCultureData(category = null) {
    try {
        let url = '/api/culture';
        if (category && category !== 'all') url += `?category=${category}`;
        const response = await fetch(url);
        const data = await response.json();
        allData = data;
        displayData(data);
        if (totalItemsEl) totalItemsEl.textContent = data.length;
    } catch (error) {
        console.error('Error fetching culture data:', error);
        container.innerHTML = '<div class="loading">Error loading data. Please try again.</div>';
    }
}

function displayData(data) {
    container.innerHTML = '';
    if (data.length === 0) {
        container.innerHTML = '<div class="loading">No results found. Try a different search or category.</div>';
        return;
    }
    data.forEach((item, index) => {
        const card = document.createElement('div');
        card.className = 'card';
        card.style.animationDelay = `${index * 0.05}s`;
        const imgSrc = item.image_url || getFallback(item.category);
        card.innerHTML = `
            <img src="${imgSrc}"
                 alt="${item.name}"
                 loading="lazy"
                 onerror="this.onerror=null;this.src='${getFallback(item.category)}'">
            <div class="card-content">
                <span class="card-category">${formatCategory(item.category)}</span>
                <h3>${item.name}</h3>
                <p>${item.description}</p>
                <div class="card-location">📍 ${item.location || 'India'}</div>
            </div>
        `;
        card.addEventListener('click', () => openModal(item));
        container.appendChild(card);
    });
}

function performSearch() {
    const query = searchInput.value.toLowerCase().trim();
    if (!query) { fetchCultureData(currentCategory); return; }
    let url = `/api/search?q=${encodeURIComponent(query)}`;
    if (currentCategory && currentCategory !== 'all') url += `&category=${currentCategory}`;
    fetch(url)
        .then(r => r.json())
        .then(data => {
            displayData(data);
            if (totalItemsEl) totalItemsEl.textContent = data.length;
        })
        .catch(e => console.error('Error searching:', e));
}

tabButtons.forEach(btn => {
    btn.addEventListener('click', () => {
        tabButtons.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        currentCategory = btn.dataset.category;
        fetchCultureData(currentCategory);
    });
});

function openModal(item) {
    const imgSrc = item.image_url || getFallback(item.category);
    const modalImg = document.getElementById('modal-image');
    modalImg.src = imgSrc;
    modalImg.onerror = function() { this.onerror=null; this.src = getFallback(item.category); };
    document.getElementById('modal-category').textContent = formatCategory(item.category);
    document.getElementById('modal-title').textContent = item.name;
    document.getElementById('modal-description').textContent = item.description;
    document.getElementById('modal-location').textContent = item.location || 'India';
    document.getElementById('modal-state').textContent = item.state || 'Pan-India';
    modal.style.display = 'block';
    document.body.style.overflow = 'hidden';
}

function closeModal() {
    modal.style.display = 'none';
    document.body.style.overflow = 'auto';
}

closeBtn.addEventListener('click', closeModal);
window.addEventListener('click', e => { if (e.target === modal) closeModal(); });
document.addEventListener('keydown', e => { if (e.key === 'Escape' && modal.style.display === 'block') closeModal(); });

searchInput.addEventListener('keyup', e => {
    if (e.key === 'Enter') { performSearch(); }
    else { clearTimeout(window.searchTimeout); window.searchTimeout = setTimeout(performSearch, 500); }
});
searchBtn.addEventListener('click', performSearch);

document.addEventListener('DOMContentLoaded', () => { fetchCultureData(); });
