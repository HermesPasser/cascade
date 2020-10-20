
const fs = require('fs')
const path = require('path')
const cp  = require('child_process');

const skeleton = `
<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8">
        <title>{title}</title>
        <style>
        .frame {}
        img {
            width:auto;
            height:auto;
            max-width:100%;
            max-height:100%;
            display: block;
            margin: 0 auto;
        }
        @media (orientation: landscape) { img { height:100%; } }
        @media (orientation: portrait) { img { width:100%; } }
        </style>
    </head>
    <body>
        <div class="frame">
            {images}
        </div>
    </body>
</html>
`
const imgTag = `<img src="{src}" />`

function isFolder(path : string) : string { 
    return fs.lstatSync(path).isDirectory()
}

function makeReaderFolder(foldername : string) {
    if (!fs.existsSync(foldername)) {
        fs.mkdirSync(foldername)
    }
}

function isImage(filename : string) {
    const exts = ['.png', '.jpg', '.gif', 'webp', 'bmp', 'jpeg', 'tif']
    for(var ext of exts) {
        if (filename.endsWith(ext))
            return true
    }
    return false
}

function makeIndexFile(filename : string, comicTitle : string, images : []) {
    const imgTags = images.map( (img : string) => imgTag.replace('{src}', img))   
    const htmlText = skeleton.replace('{title}', comicTitle)
    return htmlText.replace('{images}', imgTags.join("\n<br>"))
}

function start(comicfolder : string) {
    const basename = path.basename(comicfolder)
    const indexFilename = path.join(comicfolder, basename + '.html')
    //makeReaderFolder(foldername)
   
    var files = fs.readdirSync(comicfolder)
    files = files.filter( (item : string) =>  isImage(item))
    
    const textHtml = makeIndexFile(comicfolder, basename, files)
    fs.writeFileSync(indexFilename, textHtml)
    cp.exec(`start ${indexFilename}`, () => {})
}

const args = process.argv.slice(2)
if (args.length >= 1)  {
    if (!isFolder(args[0])){
        console.log(args[0] +" is not a folder")
    }
    start(args[0])
} else {
    console.log("missing comic folder argument")
}
   
