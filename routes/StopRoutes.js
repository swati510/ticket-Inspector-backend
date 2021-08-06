const express = require('express');
const fs = require("fs");
const router = express.Router();
const { PythonShell } =require("python-shell");

router.get('/:sid', async(req,res,next)=>{
        const stopId = req.params.sid;
        try {
        const options = {
            mode: 'text',
            pythonOptions: ['-u'],
            scriptPath: './routes',
            args: [stopId] //An argument which can be accessed in the script using sys.argv[1]
        };
        await PythonShell.run('get_route_plan.py', options, function (err, result){
            if (err) throw err;
            res.send(result.toString());
      });
    } catch (error) {
        res.status(404).json({message: error.message});
    }

});
module.exports = router;
