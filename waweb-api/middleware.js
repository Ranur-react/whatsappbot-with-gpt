export const logRequests = (req, res, next) => {
    console.log(`${req.method} ${req.url}`, JSON.stringify(req.body, null, 2));
    next();
};