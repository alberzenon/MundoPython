document.addEventListener('DOMContentLoaded', function() {
    var taskTitles = document.querySelectorAll('.task-title');
    taskTitles.forEach(function(title) {
        title.addEventListener('click', function() {
            var taskItem = this.closest('.list-group-item');
            taskItem.classList.toggle('completed');
        });
    });
});
