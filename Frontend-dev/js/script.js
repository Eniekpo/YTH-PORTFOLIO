// Using async/await to fetch data
async function fetchDataAsync() {
   try {
      const response = await fetch('https://jsonplaceholder.typicode.com/users'); // API call
      const data = await response.json(); // Parse the response
      if (!response.ok) {
         throw new Error(`Status: ${response.status}`); // Handle non-OK responses
      }
      const container = document.getElementById('data-container'); // Select the container
      container.innerHTML = data
         .map(user => `<p>${user.name} - ${user.email}</p>`) // Display user data
         .join('');
   } catch (error) {
      console.error('Error fetching data:', error); // Log errors
   }
}
// Add event listener to button
document.getElementById('fetch-data').addEventListener('click', fetchDataAsync); // Fetch data on click