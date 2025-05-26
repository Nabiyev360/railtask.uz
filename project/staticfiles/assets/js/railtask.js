// Update task status

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.complete-checkbox').forEach(checkbox => {
        checkbox.addEventListener('change', function () {
            const status = this.checked ? 'approved' : 'returned';
            const taskId = this.dataset.id;
            const url = `/tasks/update-status/${taskId}?status=${status}`;

            fetch(url)
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Serverdan xatolik qaytdi');
                    }
                    return response.json();
                })
                .then(data => {
                    console.log(`Vazifa holati: ${data.status}`);
                })
                .catch(error => {
                    console.error('Xatolik:', error);
                    alert('Vazifa holatini yangilashda muammo yuz berdi');
                });
        });
    });
});


document.addEventListener('DOMContentLoaded', function () {
    const editButtons = document.querySelectorAll('.edit-task');
    editButtons.forEach(function (btn) {
        btn.addEventListener('click', function () {
            const taskId = this.getAttribute('data-id');
            fetch(`/tasks/${taskId}/`)
                .then(response => response.json())
                .then(data => {
                    console.log(data);
                    // Formani to'ldirish
                    document.getElementById('editTaskName').value = data.title;
                    document.getElementById('editTaskDescription').value = data.description;
                    document.getElementById('editTaskDeadline').value = data.deadline;

                    // Muhimlik darajasi
                    // document.getElementById("editTaskDegree").value = data.degree;

                    // Ijrochilar
                    const performersSelect = document.getElementById('editTaskPerformers');
                    [...performersSelect.options].forEach(opt => {
                        opt.selected = data.performers.includes(parseInt(opt.value));
                    });

                    // Forma action-ni o'zgartirish
                    document.querySelector('#editTask form').action = `/tasks/edit/${taskId}`;
                })
                .catch(error => {
                    console.error('Xatolik:', error);
                });
        });
    });
});


document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".edit-task").forEach(function (button) {
        button.addEventListener("click", function () {
            const taskId = this.getAttribute("data-id");
            document.querySelector("#deadlineExtensionRequest form").action = `/tasks/${taskId}/extend`;
            document.querySelector("#deadlineExtensionRequest form").method = `post`;
        });
    });
});


document.addEventListener('DOMContentLoaded', function () {
    const editButtons = document.querySelectorAll('.deadline-ext-set');
    editButtons.forEach(function (btn) {
        btn.addEventListener('click', function () {
            const derId = this.getAttribute('data-id');
            fetch(`/tasks/extensions/${derId}`)
                .then(response => response.json())
                .then(data => {
                    document.getElementById('der_deadline').value = data.der_deadline;
                    document.getElementById('der_reason').value = data.der_reason;

                    // Forma action-ni o'zgartirish
                    document.querySelector('#deadlineExtensionSet form').action = `/tasks/extensions/${derId}/approve`;
                    document.querySelector('#reject_ext_deadline').href = `/tasks/extensions/${derId}/reject`;
                })
                .catch(error => {
                    console.error('Xatolik:', error);
                });
        });
    });
});

function updateTaskStatus(taskId, status) {
    fetch(`/tasks/update-status/${taskId}?status=${status}`, {
        method: 'GET',
        headers: {
            'X-Requested-With': 'XMLHttpRequest', // optional
        },
    })
    .then(response => {
        if (response.ok) {
            return response.json(); // Agar JSON qaytarilsa
        } else {
            throw new Error('Statusni yangilashda xatolik yuz berdi');
        }
    })
    .then(data => {
        alert(data.message || "Vazifa holati yangilandi");
        location.reload(); // Yoki kerakli UI ni yangilang
    })
    .catch(error => {
        console.error(error);
        alert("Xatolik: " + error.message);
    });
}


// // Fayl boshlanishida pond obyektini global qilish
// let pond = null;
//
// document.addEventListener("DOMContentLoaded", function () {
//     const pondInput = document.getElementById("answer_file_input");
//     if (pondInput) {
//         pond = FilePond.create(pondInput, {
//             instantUpload: false, // Fayl darhol yuborilmasin
//         });
//     }
// });



