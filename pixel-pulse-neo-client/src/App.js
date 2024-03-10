import React from 'react';
import { BrowserRouter as Router, Route, Routes, Link } from 'react-router-dom';
import CommandList from './components/CommandList';
import ScheduleViewer from './components/ScheduleViewer';
import PlaylistViewer from './components/PlaylistViewer';
import StatusViewer from './components/StatusViewer';
import CommandControl from './components/CommandControl';
import { AppBar, Toolbar, Button } from '@mui/material';
import TouchAppIcon from '@mui/icons-material/TouchApp';
import TableRowsIcon from '@mui/icons-material/TableRows';
import PlaylistAddCheckIcon from '@mui/icons-material/PlaylistAddCheck';
import SettingsSuggestIcon from '@mui/icons-material/SettingsSuggest';

function App() {
    return (
        <Router>
            <AppBar position="static">
                <Toolbar>
                    <Button color="inherit" component={Link} to="/web/commands" startIcon={<TouchAppIcon />} size="small">
                        Commands
                    </Button>
                    <Button color="inherit" component={Link} to="/web/schedule" startIcon={<TableRowsIcon />} size="small">
                        Queue
                    </Button>
                    <Button color="inherit" component={Link} to="/web/playlists" startIcon={<PlaylistAddCheckIcon />} size="small">
                        Playlists
                    </Button>
                    <Button color="inherit" component={Link} to="/web/status" startIcon={<SettingsSuggestIcon />} size="small">
                        System
                    </Button>
                </Toolbar>
            </AppBar>
            <Routes>
                <Route path="/web/commands" element={<CommandList />} />
                <Route path="/web/schedule" element={<ScheduleViewer />} />
                <Route path="/web/playlists" element={<PlaylistViewer />} />
                <Route path="/web/status" element={<StatusViewer />} />
                <Route path="/web/control/:commandName" element={<CommandControl />} />
            </Routes>
        </Router>
    );
}

export default App;
