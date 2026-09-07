/* ================================================================= */
/* Professional Calendar Interactive Controller                      */
/* ================================================================= */

document.addEventListener("DOMContentLoaded", function() {
    const daysGrid = document.getElementById("calendarDaysGrid");
    const monthYearTitle = document.getElementById("currentMonthYear");
    const modal = document.getElementById("taskModal");
    const closeModalBtn = document.getElementById("closeModalBtn");
    const cancelModalBtn = document.getElementById("cancelModalBtn");
    
    // Form fields & elements
    const selectedDateInput = document.getElementById("selectedDateInput");
    const taskIdInput = document.getElementById("taskIdInput");
    const taskTitleInput = document.getElementById("taskTitle");
    const taskCategorySelect = document.getElementById("taskCategory");
    const taskTimeInput = document.getElementById("taskTime");
    const taskDescriptionInput = document.getElementById("taskDescription");
    const modalTitleText = document.getElementById("modalTitleText");
    const saveBtnText = document.getElementById("saveBtnText");

    let currentDate = new Date();

    function renderCalendar() {
        const year = currentDate.getFullYear();
        const month = currentDate.getMonth();

        // Set header title
        const monthNames = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
        monthYearTitle.textContent = `${monthNames[month]} ${year}`;

        daysGrid.innerHTML = "";

        // Get first day and total days of the month
        const firstDayIndex = (new Date(year, month, 1).getDay() + 6) % 7; // Adjust for Monday start
        const totalDays = new Date(year, month + 1, 0).getDate();
        const prevTotalDays = new Date(year, month, 0).getDate();

        // Render previous month trailing days
        for (let i = firstDayIndex; i > 0; i--) {
            const dayCell = document.createElement("div");
            dayCell.className = "calendar-day-cell other-month";
            dayCell.innerHTML = `<div class="calendar-day-number">${prevTotalDays - i + 1}</div>`;
            daysGrid.appendChild(dayCell);
        }

        // Render current month days
        const today = new Date();
        for (let i = 1; i <= totalDays; i++) {
            const dayCell = document.createElement("div");
            dayCell.className = "calendar-day-cell";
            
            // Format current cell date string (YYYY-MM-DD)
            const formattedDate = `${year}-${String(month + 1).padStart(2, '0')}-${String(i).padStart(2, '0')}`;

            // Check if it is today
            if (i === today.getDate() && month === today.getMonth() && year === today.getFullYear()) {
                dayCell.classList.add("today");
            }

            let cellHTML = `<div class="calendar-day-number">${i}</div>`;

            // Filter tasks matching this specific date and render them as chips with data-id
            if (typeof serverTasks !== 'undefined') {
                const dayTasks = serverTasks.filter(task => task.date === formattedDate);
                dayTasks.forEach(task => {
                    cellHTML += `<div class="cal-task-chip" data-task-id="${task.id}" title="${task.title}">${task.time ? task.time + ' - ' : ''}${task.title}</div>`;
                });
            }

            dayCell.innerHTML = cellHTML;
            
            // Event listener to open modal on clicking a specific day or task
            dayCell.addEventListener("click", function(e) {
                const taskChip = e.target.closest('.cal-task-chip');
                
                if (taskChip) {
                    // Edit Mode: Clicked on an existing task
                    e.stopPropagation(); // Prevent dayCell click from firing
                    const taskId = taskChip.getAttribute('data-task-id');
                    const targetTask = serverTasks.find(t => t.id === taskId);
                    
                    if (targetTask) {
                        taskIdInput.value = targetTask.id;
                        selectedDateInput.value = targetTask.date;
                        taskTitleInput.value = targetTask.title;
                        taskCategorySelect.value = targetTask.category;
                        taskTimeInput.value = targetTask.time || '';
                        taskDescriptionInput.value = targetTask.description || '';
                        
                        modalTitleText.textContent = "Edit Task / Appointment";
                        saveBtnText.textContent = "Update Event";
                        modal.classList.add("active");
                    }
                } else {
                    // Add Mode: Clicked on empty space in day cell
                    taskIdInput.value = ""; // Clear ID so it creates a new task
                    selectedDateInput.value = formattedDate;
                    taskTitleInput.value = "";
                    taskCategorySelect.selectedIndex = 0;
                    taskTimeInput.value = "";
                    taskDescriptionInput.value = "";
                    
                    modalTitleText.textContent = "Add Task / Appointment";
                    saveBtnText.textContent = "Save Event";
                    modal.classList.add("active");
                }
            });

            daysGrid.appendChild(dayCell);
        }
    }

    // Navigation buttons listeners
    document.getElementById("prevMonthBtn").addEventListener("click", () => {
        currentDate.setMonth(currentDate.getMonth() - 1);
        renderCalendar();
    });

    document.getElementById("nextMonthBtn").addEventListener("click", () => {
        currentDate.setMonth(currentDate.getMonth() + 1);
        renderCalendar();
    });

    document.getElementById("todayBtn").addEventListener("click", () => {
        currentDate = new Date();
        renderCalendar();
    });

    // Modal close triggers
    const closeModal = () => modal.classList.remove("active");
    closeModalBtn.addEventListener("click", closeModal);
    cancelModalBtn.addEventListener("click", closeModal);

    // Initial render call
    renderCalendar();
});