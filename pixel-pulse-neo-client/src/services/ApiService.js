import axios from 'axios';

const BASE_URL = 'http://localhost:5000';

export default class ApiService {
    static getCommands() {
        return axios.get(`${BASE_URL}/commands`).then(res => res.data);
    }

    static getSchedule() {
        return axios.get(`${BASE_URL}/schedule`).then(res => res.data);
    }
    
    static setSchedule(schedule) {
        console.log("save Schdule " + schedule)
        return axios.post(`${BASE_URL}/schedule`, schedule)
        .then(response => response.data)
        .catch(error => {
            // Handle errors here, such as displaying a notification to the user
            console.error('Error updating schedule:', error);
            throw error; // Re-throw the error for further handling if necessary
        });

    }
    
    static downloadScreenshot(commandName, screenshotName) {
        const url = `${BASE_URL}/screenshots/${commandName}/${screenshotName}`;
        return axios.get(url, { responseType: 'blob' }).then(response => {
            const fileURL = window.URL.createObjectURL(new Blob([response.data]));
            const fileLink = document.createElement('a');
            fileLink.href = fileURL;
            fileLink.setAttribute('download', screenshotName); // Set the download attribute to the screenshot name
            document.body.appendChild(fileLink);
            fileLink.click();
            document.body.removeChild(fileLink);
            window.URL.revokeObjectURL(fileURL);
        });
    }

}

