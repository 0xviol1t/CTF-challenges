const fs = require('fs');
const express = require('express');
const router = express.Router();
const { triggerXSS } = require('../bot');
const { Store } = require('express-session');
function isAuthenticated(req, res, next) {
    if (req.session.user) {
        next();
    } else {
        res.redirect('/login');
    }
}
module.exports = (users,posts,store,AdminPassWord,PrivilegedPassWord) => {

    const ROLES = {
        PLAIN: "plain",
        PRIVILEGED: "privileged",
        ADMIN: "admin",
    };

    router.get('/register', (req, res) => {
        res.sendFile('register.html', { root: './views' });
    });

    router.post('/register', (req, res) => {
        const { username, password, role } = req.body;
        const userExists = users.some(u => u.username === username);
        if (userExists) {
            return res.send('Username already exists!');
        }
        users.push({ username, password, role: "plain" });
        res.redirect('/login');
    });
    router.get('/login', (req, res) => {
        res.sendFile('login.html', { root: './views' });
    });

    router.post('/login', (req, res) => {
        const { username, password } = req.body;
        console.log(username);
        console.log(password);
        const user = users.find(u => u.username === username && u.password === password);
        if (user) {
            req.session.user = user;
            res.redirect('/');
        } else {
            res.send('Invalid credentials!');
        }
    });
    router.get('/', isAuthenticated, (req, res) => {
        const currentUser = req.session.user;
        let filteredPosts = [];
        if (currentUser.role === ROLES.ADMIN) {
            filteredPosts = posts.filter(p => p.role === ROLES.PRIVILEGED || p.role === ROLES.ADMIN);
        } else if (currentUser.role === ROLES.PRIVILEGED) {
            filteredPosts = posts.filter(p => p.role === ROLES.PLAIN || p.role === ROLES.PRIVILEGED);
        } else {
            filteredPosts = posts.filter(p => p.role === ROLES.PLAIN);
        }
        res.render(`${currentUser.role}`, { posts: filteredPosts, user: currentUser });
    });
    router.post('/post', isAuthenticated, (req, res) => {
        let { content } = req.body;
    
        const scriptTagRegex = /<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi;
        content = content.replace(scriptTagRegex, '[XSS attempt blocked]');

        const eventHandlerRegex = /on\w+\s*=\s*(["']).*?\1/gi;
        content = content.replace(eventHandlerRegex, '[XSS attempt blocked]');
    
        const javascriptURLRegex = /(?:href|src)\s*=\s*(["'])\s*javascript:.*?\1/gi;
        content = content.replace(javascriptURLRegex, '[XSS attempt blocked]');
    
        const dataURLRegex = /(?:href|src)\s*=\s*(["'])\s*data:.*?\1/gi;
        content = content.replace(dataURLRegex, '[XSS attempt blocked]');
    
        const cssExpressionRegex = /style\s*=\s*(["']).*?expression\([^>]*?\).*?\1/gi;
        content = content.replace(cssExpressionRegex, '[XSS attempt blocked]');
    
        const dangerousTagsRegex = /<\/?(?:iframe|object|embed|link|meta|svg|base|source|form|input|video|audio|textarea|button|frame|frameset|applet)[^>]*?>/gi;
        content = content.replace(dangerousTagsRegex, '[XSS attempt blocked]');
    
        const dangerousAttributesRegex = /\b(?:style|srcset|formaction|xlink:href|contenteditable|xmlns)\s*=\s*(["']).*?\1/gi;
        content = content.replace(dangerousAttributesRegex, '[XSS attempt blocked]');
    
        const dangerousProtocolsRegex = /(?:href|src)\s*=\s*(["'])(?:\s*javascript:|vbscript:|file:|data:|filesystem:).*?\1/gi;
        content = content.replace(dangerousProtocolsRegex, '[XSS attempt blocked]');
    
        const dangerousFunctionsRegex = /\b(?:eval|alert|prompt|confirm|console\.log|Function)\s*\(/gi;
        content = content.replace(dangerousFunctionsRegex, '[XSS attempt blocked]');
    
        posts.push({ content: content, username: req.session.user.username, role: req.session.user.role });
        res.redirect('/');
    });
    
    
    router.get('/logout', (req, res) => {
        req.session.destroy();
        res.redirect('/login');
    });
    router.get('/report_admin', async (req, res) => {
        try {
            await triggerXSS("admin",AdminPassWord);
            res.send(`Admin Bot successfully logged in.`);
        } catch (error) {
            console.error('Error Reporting:', error);
            res.send(`Admin Bot successfully logged in.`);
        }
    });
    router.get('/report_privileged', async (req, res) => {
        try {
            await triggerXSS("privileged",PrivilegedPassWord);
            res.send(`Privileged Bot successfully logged in.`);
        } catch (error) {
            console.error('Error Reporting:', error);
            res.send(`Privileged Bot successfully logged in.`);
        }
    });
    router.get('/store', async (req, res) => {
        return res.status(200).json(store);
    });
    router.post('/store', async (req, res) => {
        if (req.body) {
            store.push(req.body);
            return res.status(200).send('Data stored successfully');
        } else {
            return res.status(400).send('No data received');
        }
    });
    router.get('/flag', async (req, res) => {
        try {
            if (req.session.user && req.session.user.role === "admin") {
                fs.readFile('/flag', 'utf8', (err, data) => {
                    if (err) {
                        console.error('Error reading flag file:', err);
                        return res.status(500).send('Internal Server Error');
                    }
                    res.send(`Your Flag Here: ${data}`);
                });
            } else {
                res.status(403).send('Unauthorized!');
            }
        } catch (error) {
            console.error('Error fetching flag:', error);
            res.status(500).send('Internal Server Error');
        }
    });
    return router;
};
