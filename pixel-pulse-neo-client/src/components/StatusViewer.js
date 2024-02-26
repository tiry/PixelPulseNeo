import React, { useEffect, useState } from 'react';
import ApiService from '../services/ApiService';
import { Container, Grid, Paper, Typography, Button, ButtonGroup, Box } from '@mui/material';
import MemoryIcon from '@mui/icons-material/Memory';
import ThermostatIcon from '@mui/icons-material/Thermostat';
import SpeedIcon from '@mui/icons-material/Speed';
import StorageIcon from '@mui/icons-material/Storage';
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import BatterySaverIcon from '@mui/icons-material/BatterySaver';
import BedtimeIcon from '@mui/icons-material/Bedtime';
import AlarmOnIcon from '@mui/icons-material/AlarmOn';

const metricIcons = {
    cpu_freq: <SpeedIcon />,
    python_cpu: <SpeedIcon />,
    cpu_temp: <ThermostatIcon />,
    gpu_temp: <ThermostatIcon />,
    free_mem: <MemoryIcon />,
    used_mem: <MemoryIcon />,
    total_mem: <MemoryIcon />,
    cpu_load1: <SpeedIcon />,
    cpu_load5: <SpeedIcon />,
    cpu_load15: <SpeedIcon />,
    up_time: <AccessTimeIcon />,
    governor : <BatterySaverIcon/>,
    
  };

const StatusViewer = () => {
    const [data, setData] = useState(null);
  
    useEffect(() => {
      const fetchData = async () => {
        ApiService.getMetrics().then(setData)
        //const response = await fetch('http://127.0.0.1:5000/api/status');
        //const jsonData = await response.json();
        //setData(jsonData);
      };
  
      fetchData().catch(console.error);
    }, []);
  
    if (!data) {
      return <Typography>Loading...</Typography>;
    }
  
    const handleSleep = () => {
      console.log("Sleep")
      ApiService.sleep()
    };

    const handleWakeup = () => {
      console.log("Wake up !")
      ApiService.wakeup()
    };
    
    return (
        <Container maxWidth="lg" >
          
          <Typography variant="h4" component="h4"> Power Management: </Typography>

          <ButtonGroup variant="contained" aria-label="Basic button group" fullWidth>
            <Button variant="contained" color="primary" startIcon={<BedtimeIcon />}
                    onClick={() => handleSleep()}>Sleep
            </Button>
            <Box width="10%"/>
            <Button variant="contained" color="primary" startIcon={<AlarmOnIcon />}
                    onClick={() => handleWakeup()}>Wake Up
            </Button>
          </ButtonGroup>
          <Typography variant="h4" component="h4"> Monitoring: </Typography>
        <Grid container spacing={3}>
          {Object.entries(data).map(([key, value]) => (
            <Grid item xs={12} sm={6} md={3} key={key}>
              <Paper elevation={2} sx={{ padding: 2, display: 'flex', alignItems: 'center', gap: 2 }}>
                {metricIcons[key] || <StorageIcon />} {/* Fallback to a default icon if specific one is not found */}
                <div>
                  <Typography variant="h6" component="h2" gutterBottom>
                    {key.replace(/_/g, ' ')}
                  </Typography>
                  <Typography variant="body1">{value}</Typography>
                </div>
              </Paper>
            </Grid>
          ))}
        </Grid>
      </Container>
    );
  };
  
export default StatusViewer;
