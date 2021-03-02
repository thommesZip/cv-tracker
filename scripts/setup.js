var spawnSync = require('child_process').spawnSync


var FAILURE = 'failure'
var SUCCESS = 'success'

var styles = {
  success: {open: '\u001b[32;1m', close: '\u001b[0m'},
  error: {open: '\u001b[31;1m', close: '\u001b[0m'},
  info: {open: '\u001b[36;1m', close: '\u001b[0m'},
  subtitle: {open: '\u001b[2;1m', close: '\u001b[0m'},
}

function color(modifier, string) {
  return styles[modifier].open + string + styles[modifier].close
}

function run(title, subtitle, command, options) {
  options = options || {}

  console.log(color('info', '\t' + title))
  console.log(color('subtitle', '\t' + subtitle))
  // console.log(color('subtitle', '\t running: ' + command))

  var result = spawnSync(command, {stdio: 'inherit', shell: true})

  if (result.status !== 0 && !options.ignoreFailure) {
    console.error(
      color(
        'error',
        '\t🤬  Failure: ' +
          title +
          '. Something went wrong. Please check the message.',
      ),
    )
    process.exit(result.status)
    return FAILURE
  }

  console.log(color('success', '\t😎 Success: ' + title + '\n\n'))
  return SUCCESS
}


function main() {
  var result


  result = run(
    'Creating Python Virtual Environment',
    '',
    `python3 -m venv venv
    `,
  )
  if (result === FAILURE) return

  result = run(
    'Installing Python Dependencies',
    '',
    `source venv/bin/activate \
    && pip install --upgrade pip \
    && pip install -r requirements.txt
    `,
  )
  if (result === FAILURE) return

  result = run(
    'Installing Serverless & JavaScript Dependencies',
    '',
    `npm install
    `,
  )
  if (result === FAILURE) return



}

main()