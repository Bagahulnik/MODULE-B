// D:\MODULE B\static\js\categories.js

// Модальное окно
function openModal(id) {
    const modal = document.getElementById(id);
    modal.classList.add('open');
}

function closeModal(id) {
    const modal = document.getElementById(id);
    modal.classList.remove('open');
}

// Открыть модалку добавления
function openAddModal() {
    document.getElementById('add-name').value = '';
    document.getElementById('add-error').style.display = 'none';
    openModal('add-modal');
}

// Открыть модалку редактирования
function openEditModal(id, name) {
    document.getElementById('edit-id').value = id;
    document.getElementById('edit-name').value = name;
    document.getElementById('edit-error').style.display = 'none';
    openModal('edit-modal');
}

// Открыть модалку удаления
let currentDeleteId = null;

function openDeleteModal(id, name) {
    currentDeleteId = id;
    document.getElementById('delete-name').textContent = name;
    document.getElementById('delete-error').style.display = 'none';
    openModal('delete-modal');
}

// Добавить категорию
document.getElementById('add-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const nameInput = document.getElementById('add-name');
    const name = nameInput.value.trim();
    const error = document.getElementById('add-error');

    error.style.display = 'none';

    if (!name) {
        error.textContent = 'Введите название категории.';
        error.style.display = 'block';
        return;
    }

    try {
        const res = await fetch('/api/categories', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name }),
        });

        const data = await res.json();

        if (!res.ok) {
            error.textContent = data.error || 'Ошибка при добавлении.';
            error.style.display = 'block';
            return;
        }

        closeModal('add-modal');
        addCategoryRow(data);
    } catch (err) {
        error.textContent = 'Не удалось соединиться с сервером.';
        error.style.display = 'block';
    }
});

function addCategoryRow(cat) {
    const tbody = document.querySelector('#categories-table tbody');
    const noCategories = document.getElementById('no-categories');

    const tr = document.createElement('tr');
    tr.id = `cat-row-${cat.id}`;
    tr.dataset.catId = cat.id;

    tr.innerHTML = `
        <td>${cat.id}</td>
        <td>${cat.name}</td>
        <td>${cat.pub_count}</td>
        <td>
            <button class="btn-edit" onclick="openEditModal(${cat.id}, '${cat.name.replace(/'/g, "\\'")}')">
                Редактировать
            </button>
            <button class="btn-danger" onclick="openDeleteModal(${cat.id}, '${cat.name.replace(/'/g, "\\'")}')">
                Удалить
            </button>
        </td>
    `;

    tbody.appendChild(tr);
    noCategories.style.display = 'none';
}

// Редактировать категорию
document.getElementById('edit-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const id = document.getElementById('edit-id').value;
    const nameInput = document.getElementById('edit-name');
    const name = nameInput.value.trim();
    const error = document.getElementById('edit-error');

    error.style.display = 'none';

    if (!name) {
        error.textContent = 'Введите название категории.';
        error.style.display = 'block';
        return;
    }

    try {
        const res = await fetch(`/api/categories/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name }),
        });

        const data = await res.json();

        if (!res.ok) {
            error.textContent = data.error || 'Ошибка при редактировании.';
            error.style.display = 'block';
            return;
        }

        closeModal('edit-modal');
        updateCategoryRow(data);
    } catch (err) {
        error.textContent = 'Не удалось соединиться с сервером.';
        error.style.display = 'block';
    }
});

function updateCategoryRow(cat) {
    const row = document.getElementById(`cat-row-${cat.id}`);
    if (!row) return;

    row.innerHTML = `
        <td>${cat.id}</td>
        <td>${cat.name}</td>
        <td>${cat.pub_count}</td>
        <td>
            <button class="btn-edit" onclick="openEditModal(${cat.id}, '${cat.name.replace(/'/g, "\\'")}')">
                Редактировать
            </button>
            <button class="btn-danger" onclick="openDeleteModal(${cat.id}, '${cat.name.replace(/'/g, "\\'")}')">
                Удалить
            </button>
        </td>
    `;
}

// Удалить категорию
async function deleteCategory() {
    const id = currentDeleteId;
    if (!id) return;

    const error = document.getElementById('delete-error');
    error.style.display = 'none';

    if (!confirm('Подтвердите удаление')) return;

    try {
        const res = await fetch(`/api/categories/${id}`, { method: 'DELETE' });

        if (!res.ok) {
            const data = await res.json();
            error.textContent = data.error || 'Ошибка удаления.';
            error.style.display = 'block';
            return;
        }

        closeModal('delete-modal');
        removeCategoryRow(id);
    } catch (err) {
        error.textContent = 'Не удалось соединиться с сервером.';
        error.style.display = 'block';
    }
}

function removeCategoryRow(id) {
    const row = document.getElementById(`cat-row-${id}`);
    if (!row) return;

    row.remove();
}
