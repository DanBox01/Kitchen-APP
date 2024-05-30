document.getElementById('add-ingredient-form').addEventListener('submit', function(event) {
    event.preventDefault();
    const name = document.getElementById('name').value;
    const quantity = document.getElementById('quantity').value;
    const expiration_date = document.getElementById('expiration_date').value;

    fetch('/ingredients', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            name: name,
            quantity: quantity,
            expiration_date: expiration_date
        })
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
    });
});

document.getElementById('upload-receipt-form').addEventListener('submit', function(event) {
    event.preventDefault();
    const formData = new FormData();
    formData.append('receipt', document.getElementById('receipt').files[0]);

    fetch('/upload-receipt', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
    });
});

document.getElementById('generate-meal-plan').addEventListener('click', function() {
    fetch('/meal-plan')
    .then(response => response.json())
    .then(data => {
        const mealPlanDiv = document.getElementById('meal-plan');
        mealPlanDiv.innerHTML = '';
        data.forEach(meal => {
            const mealDiv = document.createElement('div');
            mealDiv.textContent = `Day ${meal.day}: ${meal.ingredients.join(', ')}`;
            mealPlanDiv.appendChild(mealDiv);
        });
    });
});

document.getElementById('generate-grocery-list').addEventListener('click', function() {
    const ingredients = document.getElementById('grocery-ingredients').value.split(',');
    fetch(`/grocery-list?${new URLSearchParams({ ingredients: ingredients })}`)
    .then(response => response.json())
    .then(data => {
        const groceryListDiv = document.getElementById('grocery-list');
        groceryListDiv.innerHTML = '';
        data.forEach(item => {
            const itemDiv = document.createElement('div');
            itemDiv.textContent = `${item.name}: ${item.quantity}`;
            groceryListDiv.appendChild(itemDiv);
        });
    });
});
