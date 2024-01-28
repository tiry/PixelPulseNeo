import React from 'react';
import { BrowserRouter as Router, Route, Routes, Link } from 'react-router-dom';
import CommandList from './components/CommandList';
import ScheduleViewer from './components/ScheduleViewer';
import { AppBar, Toolbar, Button } from '@mui/material';

function App() {
    return (
        <Router>
            <AppBar position="static">
                <Toolbar>
                    <Button color="inherit" component={Link} to="/commands">
                        Commands
                    </Button>
                    <Button color="inherit" component={Link} to="/schedule">
                        Schedule
                    </Button>
                </Toolbar>
            </AppBar>
            <Routes>
                <Route path="/commands" element={<CommandList />} />
                <Route path="/schedule" element={<ScheduleViewer />} />
            </Routes>
        </Router>
    );
}

export default App;
