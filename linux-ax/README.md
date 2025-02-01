# Linux-AX: Atspi 2 Parser

Extends [at-spi2-examples](https://github.com/infapi00/at-spi2-examples/tree/master/typescript) to dump the entire Atspi 2 tree in an output file.

## Running

This will result in `out.txt` in the current working directory that contains the entire tree for the current desktop.

Install required dependencies.

```bash
sudo apt-get install \
  build-essential git \
  gobject-introspection \
  libgirepository1.0-dev \
  libcairo2 \
  libcairo2-dev
```

Building is only necessary once.

```bash
npm install
npm run build
npm run start
```

Original readme follows.

-------

## Atspi with GJS and Typescript

You can use write an atspi project using typescript by using vite and babel. This will transpile the typescript code into javascript which can be ran with gjs. Note that most node packages will not run in this environment.

Typescript types for gjs come from [ts-for-gir](https://github.com/gjsify/ts-for-gir). These can be npm installed since they do not depend on node.

### How to Run the Example

[`dump-tree.ts`](dump-tree.ts) dumps the accessibility hiearchy tree for a given application.

Install the packages and run the compiled output from the command line with gjs. Replace `"Firefox"` with the app name of your choice.

```bash
npm i
npm run build
gjs -m dist/main.js "Firefox"
```

The `-m` flag with gjs is used to allow ES modules.

You can also run `npm run start "Firefox"`. Note that if your npm version is packaged as a snap, you may have accessibility permission issues.
