# CV Tracker
This is a useful fun project. I wanted to know more about where my CVs go and what happens to them. Since they contain quite some links to my website, linkedIn, Gihtub etc... I thought, let´s track the link clicks!

### This repo contains: 

- A PDF generator that replaces all the links with trackable links 
- A redirect service that redirects the user from the tracking links to the actual links with utm_codes.
- A service that tries to find the Company name by their IP address


## Prerequisites

- Serverless Framework
- Python 3.x
- Node.js


## Setup
```
npm run setup
```

This will install the python virtual env & dependencies.
JavaScript Dependencies for Serverless Framework

### .env
Rename .env.sample to .env & change according to your needs.


STACK_NAME="redirect-service-test"
Name of the AWS CloudFormation Stack. Choose a unique name to make sure it does not conflict with other stacks.

#### DynamoDB Tables
REDIRECT_URLS_TABLE="redirectUrlTablexx"
REDIRECT_TRACKING_TABLE="redirectTrackingTablexx"
IP_TABLE="ipTablexx"

#### Where to redirect if a url cannot be found?
URL_NOT_FOUND_REDIRECT="https://thomaszipner.com/sorry-the-redirect-failed"

### The API key of you ipdate account
This key is for testing and actually works, but is highly rate limited. Create an account at https://ipdata.co/ to get your own API key.

IPDATA_API_KEY="test"

#### CV PDF

CV_VERSION="1.0"
Just some version number, so you can see what version was clicked.

BASE_PDF="cv-with-links.pdf"
FINAL_PDF="You Name - CV.pdf"

The name of the input PDF and the name to your output PDF. 
You can use a file path, if it isin another folder.

#### Redirect Service URL
This is the url that will replace your links from the PDF. If you do not want a custom domain, the just use the ApiGateway output from serverless after running "sls deploy"

REDIRECT_SERVICE_BASE_URL="https://rizyzb6wfb.execute-api.eu-central-1.amazonaws.com/prod-redirect-service/"

#### Custom Domain
You can use a custom domain, but theres is some more config to do.

1) Uncomment this part in serverless.yml

```
custom:
  customDomain:
    # activate this if you want to use a custom domain
    # domainName: ${env:REDIRECT_SERVICE_DOMAIN}
    # basePath: ''
    # stage: ${self:provider.stage}
    # createRoute53Record: true
```

Your TLD needs to be registered in Route 53.

Once you have your domain, request a new certificate with the AWS Certificate Manager. Note that you'll need to be in region us-east-1. This is the only region that works with API Gateway.

Then run:

```
sls create_domain
```

Now you can set 

```
REDIRECT_SERVICE_DOMAIN="rdr.yourdomain.com"
REDIRECT_SERVICE_BASE_URL="https://rdr.yourdomain.com/"
```


### Create your stack

Run:
```
source venv/bin/activate
```

to activate the Virtual Environtme, so the Servlerless Framework knows all the Python dependencies and then:

```
sls deploy
```

Lean back and watch the magic! It may take a few minutes.

### Update your .env 
Now take the first output under "endoints" and insert this as REDIRECT_SERVICE_BASE_URL in your .env file.

If you now visit that link, you should see your redirect service in action.
Since we have no links yet, you are redirected to URL_NOT_FOUND_REDIRECT.




## Let´s create a CV

Go the pdf-generator folder.
```
cd pdf-generator
```

There already is a test PDF that you can use, but you can replace it with your own. If the name or path is different, just change BASE_PDF in your .env.

To generate a new tracked PDF and the redirect links type:

``` 
python main.py "{SOME-IDENTIFIER}"
```

Replace {SOME-IDENTIFIER} with whatever makes sense to you. I usually use e.g. the name of the company or recuiter I send this CV. Besides the name in your DynamoDB, it genereates utm_codes with the utm_campaign set to a hash of {SOME-IDENTIFIER}, so if you use Google Analytics, you can see this as your campaign name. 😃

Now open your PDF (You Name - CV.pdf is in the same folder or where you specified it to be) and click some links.


### Your Tracking Data
Your tracking data lives in the DynamoDB tables. You could write an API against it to feed some frontend to make it look nice. Mayba I will do that when I have some time.

### redirectUrlTable 
Holds the info about the urls for the redirecting service.

### redirectTrackingTable
Holds the inofrmation about each click on a link, so you can see from where it came.
Additional company data gets added by the whois-service if it finds any. This is pointless if it is an ISP, but can be very interesting if it the company you just apllied to.

### ipTable 
is basically a cache for the IP lookups, so we need less API calls.