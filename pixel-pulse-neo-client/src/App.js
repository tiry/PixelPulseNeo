import React from 'react';
import { BrowserRouter as Router, Route, Routes, Link } from 'react-router-dom';
import CommandList from './components/CommandList';
import ScheduleViewer from './components/ScheduleViewer';
import PlaylistViewer from './components/PlaylistViewer';
import { AppBar, Toolbar, Button } from '@mui/material';

function App() {
    return (
        <Router>
            <AppBar position="static">
                <Toolbar>
                    <Button color="inherit" component={Link} to="/web/commands">
                        Available Commands
                    </Button>
                    <Button color="inherit" component={Link} to="/web/schedule">
                        Current Queue
                    </Button>
                    <Button color="inherit" component={Link} to="/web/playlists">
                        Playlists
                    </Button>
                </Toolbar>
            </AppBar>
            <Routes>
                <Route path="/web/commands" element={<CommandList />} />
                <Route path="/web/schedule" element={<ScheduleViewer />} />
                <Route path="/web/playlists" element={<PlaylistViewer />} />
            </Routes>
        </Router>
    );
}

export default App;
