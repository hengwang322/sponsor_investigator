import './App.css';
import React from 'react';
import logo from './logo.svg';
import Viewer from './Viewer.js';
import TextField from '@material-ui/core/TextField';
import ButtonGroup from '@material-ui/core/ButtonGroup';
import Button from '@material-ui/core/Button';
import Snackbar from '@material-ui/core/Snackbar';
import AlertTitle from '@material-ui/lab/AlertTitle';
import Alert from '@material-ui/lab/Alert';
import CircularProgress from '@material-ui/core/CircularProgress';
import Backdrop from '@material-ui/core/Backdrop';
import Card from '@material-ui/core/Card';
import vidList from './sampleVideo.json';

class App extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      value: '',
      isLoaded: false,
      showError: false,
      data: [],
      videoId: '',
      showAlert: false,
      errMsg: '',
      loading: false,
      width: window.innerWidth,
    };
  }

  onChange = (e) => {
    this.setState({
      value: e.target.value,
      showError: false
    });
  };

  onClickSubmit = () => {
    //TODO
    //Still captures other domains too. Regex sucks
    var url = this.state.value;
    var regex = /^.*(youtu\.be\/|v\/|u\/\w\/|embed\/|watch\?v=|&v=)([^#&?]*).*/;
    var match = url.match(regex);
    if (match && match[2].length === 11) {
      this.setState({ loading: true });
      this.onSubmit(match[2]);
    } else {
      this.setState({ showError: true });
    }
  };

  onSubmit = (videoId) => {
    const API = process.env.REACT_APP_SPONSOR_API;
    fetch(API, {
      method: 'POST',
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ 'vid': videoId })
    })
      .then(res => res.json())
      .then(data => {
        if (data['error'] === undefined) {
          this.setState({
            data: data['transcript'],
            videoId: data['videoId'],
            isLoaded: true,
            loading: false,
          });
        } else {
          this.showAlert(data['error']);
        }
      })
      .catch(e => this.showAlert(e.message));
  };

  showAlert = (msg) => {
    this.setState({ showAlert: true, errMsg: msg, loading: false },
      () => { setTimeout(() => { this.dismissAlert(); }, 8000); });
  };

  dismissAlert = () => {
    this.setState({ showAlert: false, errMsg: '' });
  };

  getRndInteger = (min, max) => {
    return Math.floor(Math.random() * (max - min)) + min;
  };

  onClickRandom = () => {
    this.setState({ loading: true });
    const videoId = vidList[this.getRndInteger(0, vidList.length - 1)];
    this.onSubmit(videoId);
  };

  onLoading = () => this.setState({ loading: true });

  onLoadingEnd = () => this.setState({ loading: false });

  componentDidMount() {
    window.addEventListener("resize", this.handleResize);
  }

  componentWillUnmount() {
    window.removeEventListener("resize", () => { });
  }

  handleResize = () => this.setState({ width: window.innerWidth });


  render() {
    const { width, isLoaded, loading, showError, value,
      data, videoId, showAlert, errMsg } = this.state;
    const searchWidthUnload = () => {
      if (width <= 360) { return width * 0.8; }
      else if (width >= 600) { return 560; }
      else return width * 0.8;
    };
    const searchWidthLoaded = () => {
      if (width >= 500) { return 300; }
      else return width * 0.45;
    };
    const searchStyle = isLoaded
      ? { width: searchWidthLoaded(), margin: '10px 3px 10px 1px' }
      : { width: searchWidthUnload(), margin: '10px 3px 10px 1px' };
    return (
      <div className='App'>
        {isLoaded ? undefined : <>
          <img src={logo} className="App-logo" alt="logo" style={{ margin: 20 }} />
          <h4>Detect sponsored segments in Youtube videos<br />
          With the power of machine learning!</h4>
        </>}
        <span>
          <TextField
            disabled={loading}
            error={showError}
            onFocus={this.onFocus}
            style={searchStyle}
            value={value}
            label='Youtube Link'
            variant='outlined'
            placeholder='www.youtube.com/watch?v=dQw4w9WgXcQ'
            onChange={this.onChange}
            helperText={showError
              ? 'This doesn\'t appears to be an valid link, please try again'
              : undefined}
            size={isLoaded ? 'small' : 'medium'}
          />
          {isLoaded ? undefined : <br />}
          <ButtonGroup style={{ margin: '15px 3px 10px 3px', padding: '0px 10px 0px 10px' }}>
            <Button
              variant="contained"
              color="primary"
              disabled={loading}
              onClick={this.onClickSubmit}
              size={isLoaded ? 'small' : 'large'}>
              {isLoaded ? 'Submit' : 'Submit & block sponsors!'}
            </Button>
            <Button
              variant="contained"
              color="secondary"
              disabled={loading}
              onClick={this.onClickRandom}
              size={isLoaded ? 'small' : 'large'}>
              {isLoaded ? 'Random' : 'Pick a random video for me'}
            </Button>
          </ButtonGroup>
          <br />
        </span>
        {isLoaded ? <Viewer data={data} videoId={videoId} /> : undefined}
        <Snackbar
          open={showAlert}
          anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
          style={{ textAlign: 'left' }}
        >
          <Alert
            elevation={6}
            variant="filled"
            severity="error"
            onClose={this.dismissAlert}>
            <AlertTitle>Error</AlertTitle>
            {errMsg}
          </Alert>
        </Snackbar>

        <Backdrop
          style={{ zIndex: 20 }}
          open={loading}
          onClick={this.onLoadingEnd}>
          <Card variant="outlined" style={{ padding: 40 }}>
            <CircularProgress style={{ padding: 10 }} />
            <h3>{'Loading, please wait'}</h3>
          </Card>
        </Backdrop>
      </div>
    );
  }
}

export default App;