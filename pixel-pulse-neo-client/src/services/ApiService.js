import axios from 'axios';

//const BASE_URL = 'http://localhost:5000';
//const BASE_URL = 'http://lcddriver.local:5000/api';
//const BASE_URL = 'http://localhost:5000/api';
export const BASE_URL = '/api';

export default class ApiService {

    static getCommands() {
        return axios.get(`${BASE_URL}/commands`).then(res => res.data);
    }

    static getCommand(name) {
        return axios.get(`${BASE_URL}/command/` + name).then(res => res.data);
    }

    static getCurrentCommand() {
        return axios.get(`${BASE_URL}/command`).then(res => res.data);
    }

    static executeCmd(name, duration=10, interupt=false) {
        return axios.post(`${BASE_URL}/command/` + name + "?interup=" + interupt + "&duration=" + duration).then(res => res.data);
    }
    
    static queueCmd(name) {
        return axios.post(`${BASE_URL}/command/` + name ).then(res => res.data);
    }
    static getSchedule() {
        return axios.get(`${BASE_URL}/schedule`).then(res => res.data);
    }
    
    static getPlaylist(name) {
        return axios.get(`${BASE_URL}/schedule/` + name).then(res => res.data);
    }

    static getPlaylists() {
        return axios.get(`${BASE_URL}/schedules`).then(res => res.data);
    }

    static playPlaylist(name, duration=10, interupt=false) {
        return axios.post(`${BASE_URL}/schedule/` + name + "/execute").then(res => res.data);
    }

    static getPlaylistsDetailed() {
        return axios.get(`${BASE_URL}/schedules/detailed`).then(res => res.data);
    }
    
    static sendCommandMessage(command_name, message) {
        var post= axios.post(`${BASE_URL}/message/` + command_name , message)
        return post.then(response => response.data)
        .catch(error => {
            console.error('Error updating schedule:', error);
            throw error; // Re-throw the error for further handling if necessary
        });

    }
   
    static setSchedule(schedule, name) {
        console.log("save schedule " + schedule)
        var post
        if (name)  
            post= axios.post(`${BASE_URL}/schedule/` + name , schedule)
        else
            post =axios.post(`${BASE_URL}/schedule`, schedule)
        return post.then(response => response.data)
        .catch(error => {
            // Handle errors here, such as displaying a notification to the user
            console.error('Error updating schedule:', error);
            throw error; // Re-throw the error for further handling if necessary
        });

    }
    
    static getMetrics() {
        return axios.get(`${BASE_URL}/metrics/all`).then(res => res.data);
    }

    static sleep() {
        return axios.get(`${BASE_URL}/power/sleep`).then(res => res.data);
    }

    static wakeup() {
        return axios.get(`${BASE_URL}/power/wakeup`).then(res => res.data);
    }

    static watchdog(state) {
        console.log(`${BASE_URL}/watchdog/` + state)
        return axios.post(`${BASE_URL}/watchdog/` + state).then(res => res.data);
    }

}

