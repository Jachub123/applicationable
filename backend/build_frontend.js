const { exec } = require('child_process');

console.log('Starting Angular production build...');

exec('ng build --configuration production', (error, stdout, stderr) => {
  if (error) {
    console.error(`Error: ${error.message}`);
    return;
  }
  if (stderr) {
    console.error(`stderr: ${stderr}`);
    return;
  }
  console.log(`stdout: ${stdout}`);
  console.log('Angular production build completed successfully.');
});