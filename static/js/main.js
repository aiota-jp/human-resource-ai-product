document.addEventListener('DOMContentLoaded', () => {
  const importType = document.getElementById('import_type');
  const trainingSelect = document.getElementById('training-select');
  const toggleTraining = () => {
    if (!importType || !trainingSelect) return;
    trainingSelect.style.display = importType.value === 'training' ? 'block' : 'none';
  };
  if (importType) {
    importType.addEventListener('change', toggleTraining);
    toggleTraining();
  }
});
