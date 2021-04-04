import React from 'react';
import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
import DialogContent from '@material-ui/core/DialogContent';
import DialogTitle from '@material-ui/core/DialogTitle';
import DialogContentText from '@material-ui/core/DialogContentText';
import Button from '@material-ui/core/Button';

export default function About(props) {
  return (
    <>
      <Button size='small' onClick={props.onOpen}>About</Button>
      <Dialog onClose={props.onClose} open={props.isOpen}>
        <DialogTitle>About Sponsor Investigator</DialogTitle>
        <DialogContent >
          <DialogContentText>
            <p style={{ lineHeight: 2, textAlign: 'justify' }}>
              Sponsor Investigator uses a machine learning algorithm to distinguish between
              sponsored segments & actual content. If you want to learn more, you can check
              out the <a href="https://github.com/hengwang322/sponsor_investigator">Github repository</a>.
              If you'd like to contact the author, feel free to shoot me
              an <a href="mailto:wangheng322<at>gmail.com">email</a> or contact me
              on <a href="https://www.linkedin.com/in/hengwang322/">LinkedIn</a>.<br />
              This project uses data from <a href="https://sponsor.ajay.app/">SponsorBlock</a>. Check out their
              browser extension and open API for skipping sponsor segments in YouTube videos on their website!
            </p>
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={props.onClose}>
            Close
            </Button>
        </DialogActions>
      </Dialog></>
  );
}