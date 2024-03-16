import React from 'react';
import { BrowserRouter as Router, Route, Routes, Link } from 'react-router-dom';
import CommandList from './components/CommandList';
import ScheduleViewer from './components/ScheduleViewer';
import PlaylistViewer from './components/PlaylistViewer';
import StatusViewer from './components/StatusViewer';
import CommandControl from './components/CommandControl';
import CameraControl from './components/CameraControl';
import { AppBar, Toolbar, Button, Tabs, Tab } from '@mui/material';
import TouchAppIcon from '@mui/icons-material/TouchApp';
import TableRowsIcon from '@mui/icons-material/TableRows';
import PlaylistAddCheckIcon from '@mui/icons-material/PlaylistAddCheck';
import SettingsSuggestIcon from '@mui/icons-material/SettingsSuggest';

function App() {

    const [currentTab, setCurrentTab] = React.useState(null);

    const handleTabChange = (event, newValue) => {
        setCurrentTab(newValue);
    };

    return (
        <Router>
            <AppBar position="static" >
                <Toolbar>
                    
                    <Tabs   value={currentTab}  
                            onChange={handleTabChange} 
                            TabIndicatorProps={{style: {backgroundColor:'white'}}}
                            sx={{
                                flexGrow: 1,
                                "& a:_hover" : {backgroundColor: 'white'},
                                "& a:focus" : {color: 'white'},  
                                "& a:active" : {color: 'white'}  
                            }}
                            >
                        <Tab label="Commands" 
                            icon={<TouchAppIcon />} 
                            iconPosition='start' 
                            sx={{textTransform: 'none', padding:"0px"}} 
                            component={Link} to="/web/commands">
                        </Tab>
                        <Tab label="Queue" 
                        component={Link} to="/web/schedule" 
                        icon={<TableRowsIcon />} iconPosition='start' 
                        size="small" 
                        sx={{textTransform: 'none', padding:"0px"}}>    
                        </Tab>
                        <Tab label="Playlists" 
                        component={Link} to="/web/playlists" 
                        icon={<PlaylistAddCheckIcon />} iconPosition='start' 
                        sx={{textTransform: 'none',padding:"0px"}}>
                        </Tab>
                    </Tabs>

                    <Button color="inherit" 
                        component={Link} to="/web/status" 
                        startIcon={<SettingsSuggestIcon />} size="small" 
                        onClick={() => setCurrentTab(null)}>
                    </Button>
                    
                </Toolbar>
            </AppBar>
            <Routes>
                <Route path="/web/commands" element={<CommandList />} />
                <Route path="/web/schedule" element={<ScheduleViewer />} />
                <Route path="/web/playlists" element={<PlaylistViewer />} />
                <Route path="/web/status" element={<StatusViewer />} />
                <Route path="/web/camera" element={<CameraControl />} />
                <Route path="/web/control/:commandName" element={<CommandControl />} />
            </Routes>
        </Router>
    );
}

export default App;
