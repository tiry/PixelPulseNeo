import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import {BASE_URL} from '../services/ApiService'

import ApiService from '../services/ApiService';
import { Container, Grid, TextField, Typography, Button,} from '@mui/material';

import TextIncreaseIcon from '@mui/icons-material/TextIncrease';
import TextDecreaseIcon from '@mui/icons-material/TextDecrease';
import SpeedIcon from '@mui/icons-material/Speed';
import TextRotationNoneIcon from '@mui/icons-material/TextRotationNone';
import HeightIcon from '@mui/icons-material/Height';
import TrackChangesIcon from '@mui/icons-material/TrackChanges';
import ExpandIcon from '@mui/icons-material/Expand';
//import { ColorPicker } from "@material-ui/color";
//import { ColorPicker, ColorInput } from "material-ui-color";

const CommandControl = () => {
    const [command, setCommand] = useState({});

    const [text, setText] = useState("");

    const { commandName } = useParams();

    useEffect(() => {
      ApiService.getCommand(commandName).then(setCommand)
    }, [commandName]);
  
    if (!command) {
      return <Typography>Loading...</Typography>;
    }

    const handleSendText = () => {
      console.log("Sending text " + text);
      ApiService.sendCommandMessage(commandName, text).then(() => {
        console.log("Text sent");
      })

      /*ApiService.sendText(commandName, text)
        .then(() => {
          console.log("Text sent");
        });*/
    }

    const sendCommandDelta = (cmd, value) => {
      var key_name = cmd + "_delta"
      var d = {}
      d[key_name] = value
      var msg = JSON.stringify(d)
      ApiService.sendCommandMessage(commandName, msg).then(() => {
        console.log("Command " + msg + " sent");
      })
    } 
  
    return (
        <Container maxWidth="lg" >          
          <Typography variant="h4" component="h4"> Control {commandName}: </Typography>
          <Typography variant="" component="i"> {command.description}: </Typography>
          {command.screenshots ? (
          <img src={`${BASE_URL}/screenshots/${command.name}/${command.screenshots[0]}`} width="600 px"/>
          ) : ( "no" ) }
          <Grid container spacing={2}>
                <Grid item xs={8}>
                  <TextField fullWidth
                      defaultValue={text}
                      onChange={(e) => setText(e.target.value)}>
                  </TextField>
                </Grid>
                <Grid item xs={4}>
                  <Button variant="contained" color="primary" startIcon={<TextRotationNoneIcon />}
                                    onClick={() => handleSendText()} fullWidth>
                  </Button>     
                </Grid>
          {(command.name==="scrolltext") ? (
            <>
            <Grid item xs={2}>
              <Button variant="contained" color="primary" startIcon={<TextIncreaseIcon />}
                    onClick={() => sendCommandDelta('font_height', 1)} fullWidth>
              </Button>
            </Grid>
            <Grid item xs={2}>
              <Button variant="contained" color="primary" startIcon={<SpeedIcon />}
                    onClick={() => sendCommandDelta('speed', 1)} fullWidth>+
              </Button>
            </Grid>
            <Grid item xs={2}>
              <Button variant="contained" color="primary" startIcon={<HeightIcon />}
                    onClick={() => sendCommandDelta('amplitude', 1)} fullWidth>+
              </Button>
            </Grid>
            
            <Grid item xs={2}>
              <Button variant="contained" color="primary" startIcon={<TrackChangesIcon />}
                    onClick={() => sendCommandDelta('phase_step', 0.1)} fullWidth>+
              </Button>
            </Grid>
            <Grid item xs={2}>
              <Button variant="contained" color="primary" startIcon={<ExpandIcon />}
                    onClick={() => sendCommandDelta('shift_amplitude', 1)} fullWidth>+
              </Button>
            </Grid>
            <Grid item xs={2}>
            </Grid>

            <Grid item xs={2}>
              <Button variant="contained" color="primary" startIcon={<TextDecreaseIcon />}
                    onClick={() => sendCommandDelta('font_height', -1)} fullWidth>
              </Button>
            </Grid>
            <Grid item xs={2}>
              <Button variant="contained" color="primary" startIcon={<SpeedIcon />}
                    onClick={() => sendCommandDelta('speed', -1)} fullWidth>-
              </Button>
            </Grid>
            <Grid item xs={2}>
              <Button variant="contained" color="primary" startIcon={<HeightIcon />}
                    onClick={() => sendCommandDelta('amplitude', -1)} fullWidth>-
              </Button>
            </Grid>
            <Grid item xs={2}>
              <Button variant="contained" color="primary" startIcon={<TrackChangesIcon />}
                    onClick={() => sendCommandDelta('phase_step', -0.1)} fullWidth >-
              </Button>
            </Grid>
            <Grid item xs={2}>
              <Button variant="contained" color="primary" startIcon={<ExpandIcon />}
                    onClick={() => sendCommandDelta('shift_amplitude', -1)} fullWidth >-
              </Button>
            </Grid>
            <Grid item xs={2}>
            </Grid>
            
            </>
          ) : (<></>)} 
          </Grid>

      </Container>
    );
  };
  
export default CommandControl;
