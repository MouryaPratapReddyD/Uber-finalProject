import { useHistory } from 'react-router-dom'
import { saveAuthorisation, isAuthorised } from '../../utils/auth'
//import { useIntl } from 'react-intl'
//import Page from 'material-ui-shell/lib/containers/Page/Page'
import React, { useState, useContext } from 'react'
import TextField from '@material-ui/core/TextField'
import Typography from '@material-ui/core/Typography'
import { makeStyles } from '@material-ui/core/styles'
import Button from '@material-ui/core/Button'
//import Button from 'material-ui/Button'
import Paper from '@material-ui/core/Paper'
//import MenuContext from 'material-ui-shell/lib/providers/Menu/Context'

const useStyles = makeStyles((theme) => ({
  paper: {
    width: 'auto',
    marginLeft: theme.spacing(3),
    marginRight: theme.spacing(3),
    [theme.breakpoints.up(620 + theme.spacing(6))]: {
      width: 400,
      marginLeft: 'auto',
      marginRight: 'auto',
    },
    marginTop: theme.spacing(8),
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    padding: `${theme.spacing(2)}px ${theme.spacing(3)}px ${theme.spacing(
      3
    )}px`,
  },
  avatar: {
    margin: theme.spacing(1),
    width: 192,
    height: 192,
    color: theme.palette.secondary.main,
  },
  form: {
    marginTop: theme.spacing(1),
  },
  submit: {
    margin: theme.spacing(3, 0, 2),
  },
  container: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    height: `100%`,
  },
}))

const addUser = async (username, password) => {
  console.log("add user signup")
  const paramdict = {
    'username': username,
    'password': password
  }

  try {
    const config = {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(paramdict)
    }


    //const response = await fetch("http://localhost:5000/register", config);
    const response = await fetch("/register", config);
    //const response = await fetch(`${process.env.REACT_APP_API_SERVICE_URL}:5000/register`, config);
    //const json = await response.json()
    if (response.ok) {
        //return json
        //return response
        console.log("success on send.");
        
    } else {
        alert("response: " + response.toString());
    }

    try {
      const data = await response.json();
      console.log("on reply:")
      alert("User " + data["username"] + " registered successfully")


      // back to landing page!
      //history.push("/");
    } catch (err) {
      console.log(err);
      alert("exception on reply!");
    }

  } catch (error) {
    console.log(error);
    alert("exception on send");
  }
};

const SignUp = () => {
  const classes = useStyles()
  //const intl = useIntl()
  const history = useHistory()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  //const { setAuthMenuOpen } = useContext(MenuContext)

  function handleSubmit(event) {
    event.preventDefault()

    // fwo: register new user!
    console.log(username)
    console.log(password)
    //.. return userid

    addUser(username, password)
    setUsername('')
    setPassword('')

    // save more: name, group, userid
    // authenticate({
    //   displayName: 'User',
    //   email: username,
    // })
  }

  const authenticate = (user) => {
    saveAuthorisation(user)
    let _location = history.location
    let isAuth = isAuthorised()
    //setAuthMenuOpen(false)
    if (isAuth) {
      let _route = '/home'
      if (_location.state && _location.state.from) {
        _route = _location.state.from.pathname
        history.push(_route)
      } else {
        history.push(_route)
      }
    }
  }

  return (
    
    <React.Fragment>
      <Paper className={classes.paper} elevation={6}>
        <div className={classes.container}>
          <Typography component="h1" variant="h5">
            {'Sign up'}
          </Typography>
          <form className={classes.form} onSubmit={handleSubmit} noValidate>
            <TextField
              value={username}
              onInput={(e) => setUsername(e.target.value)}
              variant="outlined"
              margin="normal"
              required
              fullWidth
              id="username"
              label={'Username'}
              name="username"
              autoComplete="username"
              autoFocus
            />
            <TextField
              value={username}
              onInput={(e) => setUsername(e.target.value)}
              variant="outlined"
              margin="normal"
              required
              fullWidth
              id="email"
              label={'E-Mail'}
              name="email"
              autoComplete="email"
            />
            <TextField
              value={password}
              onInput={(e) => setPassword(e.target.value)}
              variant="outlined"
              margin="normal"
              required
              fullWidth
              name="password"
              label={'Password'}
              type="password"
              id="password"
              autoComplete="current-password"
            />
            <TextField
              value={password}
              onInput={(e) => setPassword(e.target.value)}
              variant="outlined"
              margin="normal"
              required
              fullWidth
              name="password_confirm"
              label={'Confirm Password'}
              type="password"
              id="password_confirm"
              autoComplete="current-password"
            />
            <Button
              type="submit"
              fullWidth
              variant="contained"
              color="primary"
              className={classes.submit}
            >
              {'Sign up'}
            </Button>
          </form>
        </div>
      </Paper>
    </React.Fragment>
  )
}

export default SignUp
