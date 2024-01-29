import axios from 'axios';

//const BASE_URL = 'http://localhost:5000';
const BASE_URL = '';

export default class ApiService {
    static getCommands() {
        return axios.get(`${BASE_URL}/commands`).then(res => res.data);
    }

    static executeCmd(name) {
        return axios.post(`${BASE_URL}/command/` + name).then(res => res.data);
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
    

}

