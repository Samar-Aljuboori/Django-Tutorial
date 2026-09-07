// Global JavaScript Controller for Deletion Modal
let formToSubmit = null;
const modal = document.getElementById('globalDeleteModal');
const confirmBtn = document.getElementById('confirmDeleteBtn');
const cancelBtn = document.getElementById('cancelDeleteBtn');

// Listen for click events across the entire document to catch delete triggers
document.addEventListener('click', function(e) {
    // Check if the clicked element or its parent is a delete button
    const deleteBtn = e.target.closest('.btn-delete, .delete-btn-icon, [data-confirm-delete]');
    
    if (deleteBtn) {
        // Find the parent form associated with this delete button
        const form = deleteBtn.closest('form');
        if (form) {
            e.preventDefault(); 
            e.stopPropagation();
            formToSubmit = form; 
            
            // Reset confirm button state every time the modal opens
            if (confirmBtn) {
                confirmBtn.disabled = false;
                confirmBtn.innerHTML = 'Delete';
                confirmBtn.style.opacity = '1';
            }
            
            // Display the modal with the blur effect overlay
            if (modal) {
                modal.style.display = 'flex';
            }
        }
    }
});

// Handle cancel button click event to close the modal
if (cancelBtn) {
    cancelBtn.addEventListener('click', function() {
        if (modal) {
            modal.style.display = 'none';
        }
        formToSubmit = null;
    });
}

// Handle confirmation delete button click event (prevent multi-click and show status)
if (confirmBtn) {
    confirmBtn.addEventListener('click', function() {
        if (formToSubmit) {
            // Disable button to prevent multiple clicks and indicate the process is running
            confirmBtn.disabled = true;
            confirmBtn.innerHTML = 'Deleting...';
            confirmBtn.style.opacity = '0.7';
            
            // Submit the targeted form
            formToSubmit.submit();
        }
    });
}