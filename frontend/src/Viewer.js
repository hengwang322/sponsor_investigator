import React from 'react';
import YouTube from 'react-youtube';
import Switch from '@material-ui/core/Switch';
import Card from '@material-ui/core/Card';
import Grid from '@material-ui/core/Grid';
import InfoIcon from '@material-ui/icons/Info';
import Tooltip from '@material-ui/core/Tooltip';
import { withStyles } from '@material-ui/core/styles';

class Viewer extends React.Component {
  constructor(props) {
    super(props);
    this.scrollCount = 0;
    this.scrollTimer = '';
    this.state = {
      isScroll: true,
      segment: -1,
      player: undefined,
      currentTime: 0,
      videoId: '',
      data: [],
      width: window.innerWidth,
      height: window.innerHeight
    };
  }

  onPlayerReady = (e) => {
    e.target.pauseVideo();
    this.setState({ player: e.target });
  };

  onUpdateSegment = () => {
    var i;
    var currentTime = 0;
    if (this.state.player) { currentTime = this.state.player.getCurrentTime(); };
    for (i = 0; i < this.state.data.length; i++) {
      if (this.state.data[i]['start'] > currentTime) {
        this.setState({ segment: i === 0 ? 0 : i - 1 });
        if (this.state.isScroll) {
          document.getElementById(this.state.segment)
            .scrollIntoView({ block: 'center' });
        }
        break;
      }
    }
  };

  startInterval = () => { this.interval = setInterval(this.onUpdateSegment, 200); };

  endInterval = () => { clearInterval(this.interval); };

  componentDidMount() {
    this.setState({ segment: -1, data: this.props.data });
    document.getElementById('text-container')
      .addEventListener('scroll', this.handleScroll);
    window.addEventListener("resize", this.handleResize);
  }

  componentWillUnmount() {
    clearInterval(this.interval);
    document.getElementById('text-container')
      .removeEventListener('scroll', () => { });
    window.removeEventListener("resize", () => { });
  }

  handleResize = () => {
    this.setState({ width: window.innerWidth, height: window.innerHeight });
  };

  componentDidUpdate(prevProps) {
    const props = this.props;
    if (props.videoId !== prevProps.videoId) {
      this.setState({
        videoId: props.videoId,
        data: props.data,
        segment: -1
      });
      document.getElementById('text-container').scrollTo(0, 0);
    };
  }

  onSwitchScroll = () => {
    this.setState({ isScroll: !this.state.isScroll });
  };

  handleScroll = () => {
    // if scrolling several times in a short period of time, 
    // as an acutal user would do, switch off auto scrolling
    this.scrollCount++;
    if (this.scrollCount <= 5) {
      this.scrollTimer = setTimeout(function () {
        this.scrollCount = 0;
      }.bind(this), 500);
    } else if (this.scrollCount >= 6) {
      clearTimeout(this.scrollTimer);
      this.scrollCount = 0;
      this.setState({ isScroll: false });
    }
  };

  onClickSegment = (i) => {
    const player = this.state.player;
    const seekTime = this.state.data[i]['start'];
    player.seekTo(seekTime);
  };


  render() {
    const { width, height, data, segment, isScroll } = this.state;
    const arrAvg = arr => arr.reduce((a, b) => a + b, 0) / arr.length;
    const makeColor = (opacity = 1) => `rgba(100,149,237, ${opacity})`;
    const text = data.map(
      (item, index) => {
        const isBold = segment === index ? "bold" : "normal";
        const color = makeColor(arrAvg(item['label']));
        return <div key={index} style={{ paddingTop: 3 }}>
          <span
            onClick={() => { this.onClickSegment(index); }}
            className='clickable-text'
            id={index}
            style={{ backgroundColor: color, width: 450, fontWeight: isBold }}>
            {item['text']}
          </span>
        </div>;
      });

    const cardHeight = (height < 800) ? (height * 0.8) : (height * 0.85);
    const cardWidth = (width < 500) ? (width * 0.9) : 500;
    const HtmlTooltip = withStyles(() => ({
      tooltip: {
        backgroundColor: 'white',
        color: 'black',
        fontSize: 15,
        border: '1px solid #dadde9',
        maxWidth: 450
      },
    }))(Tooltip);

    const tooltip = <React.Fragment>
      <p style={{ margin: 10, lineHeight: 1.75 }}>
        {'Sponsored segments are highlighted in '}
        <span style={{ backgroundColor: 'rgb(100,149,237)' }}>{'blue'}</span>{'. '}<br />
        {'Darker color indicates higher confidence.'} <br />
        {'Current transcript is marked in '}<strong>{'bold'}</strong>. <br />
        {'Click on a transcript to jump to the section in the video.'}<br />
        {'You can enable auto scroll to keep transcript in sync with the video.'}
      </p>
    </React.Fragment>;
    return (
      <div>
        <Card style={{
          margin: "auto", padding: 10,
          width: cardWidth, height: cardHeight
        }}>
          <YouTube
            videoId={this.props.videoId}
            opts={{ height: 260, width: cardWidth }}
            onReady={this.onPlayerReady}
            onPause={this.endInterval}
            onPlay={this.startInterval}
          />
          <Card variant="outlined" style={{ backgroundColor: 'rgb(250,250,250)', margin: 5 }}>
            <Grid container direction='row' justify='flex-start' alignItems='center'>
              <Grid item xs spacing={3}>
                <span style={{ margin: 5, float: 'left' }}>
                  <h3 style={{ margin: 0, float: 'left' }}>{'Transcript: '}</h3>
                  <HtmlTooltip title={tooltip}>
                    <InfoIcon color='action' style={{ marginLeft: 3, fontSize: 25 }} />
                  </HtmlTooltip>
                </span>
              </Grid>
              <Grid item xs spacing={3}>
                <span style={{ margin: 5, float: 'right' }}>
                  {'Enable Auto Scroll?'}
                  <Switch
                    checked={isScroll}
                    onChange={this.onSwitchScroll}
                    size='small'
                  />
                </span>
              </Grid>
            </Grid>
            <div
              id='text-container'
              style={{ height: (cardHeight - 350), overflowY: 'scroll', padding: 10 }}
            >
              <span id={-1} />
              {text}
            </div>
          </Card>

        </Card>
      </div>
    );
  }
}

export default Viewer;