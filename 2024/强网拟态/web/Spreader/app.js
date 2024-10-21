const express = require('express');
const session = require('express-session');
const stringRandom = require('string-random');
const bodyParser = require('body-parser');
const app = express();
const port = 3000;
const AdminPassWord=stringRandom(16, { numbers: true })
const PrivilegedPassWord=stringRandom(16, { numbers: true })
const PlainPassWord=stringRandom(16, { numbers: true })
const secret_key=stringRandom(16, { numbers: true })
const users = [];
const posts = [];
const store = [];
users.push({ username:"admin", password:AdminPassWord, role: "admin" });
users.push({ username:"privileged", password:PrivilegedPassWord, role: "privileged" });
users.push({ username:"plain", password:PlainPassWord, role: "plain" });
console.log(users)
app.use(express.static('views'));
app.set('view engine', 'ejs');
app.use(bodyParser.urlencoded({ extended: true }));
app.use(session({
    secret: secret_key,
    resave: false,
    saveUninitialized: true,
    cookie: {
        httpOnly: false,
        secure: false,
    }
}));


app.use('/', require('./routes/index')(users,posts,store,AdminPassWord,PrivilegedPassWord));

app.listen(port, () => {
    console.log(`App is running on http://localhost:${port}`);
});
