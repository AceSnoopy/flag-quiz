"""All ISO 3166-1 countries and territories: code -> (name, region)."""

_RAW = """
af|Afghanistan|Asia
ax|Åland Islands|Europe
al|Albania|Europe
dz|Algeria|Africa
as|American Samoa|Oceania
ad|Andorra|Europe
ao|Angola|Africa
ai|Anguilla|Americas
aq|Antarctica|Antarctica
ag|Antigua and Barbuda|Americas
ar|Argentina|Americas
am|Armenia|Asia
aw|Aruba|Americas
au|Australia|Oceania
at|Austria|Europe
az|Azerbaijan|Asia
bs|Bahamas|Americas
bh|Bahrain|Asia
bd|Bangladesh|Asia
bb|Barbados|Americas
by|Belarus|Europe
be|Belgium|Europe
bz|Belize|Americas
bj|Benin|Africa
bm|Bermuda|Americas
bt|Bhutan|Asia
bo|Bolivia|Americas
bq|Caribbean Netherlands|Americas
ba|Bosnia and Herzegovina|Europe
bw|Botswana|Africa
bv|Bouvet Island|Antarctica
br|Brazil|Americas
io|British Indian Ocean Territory|Asia
bn|Brunei|Asia
bg|Bulgaria|Europe
bf|Burkina Faso|Africa
bi|Burundi|Africa
cv|Cape Verde|Africa
kh|Cambodia|Asia
cm|Cameroon|Africa
ca|Canada|Americas
ky|Cayman Islands|Americas
cf|Central African Republic|Africa
td|Chad|Africa
cl|Chile|Americas
cn|China|Asia
cx|Christmas Island|Oceania
cc|Cocos (Keeling) Islands|Oceania
co|Colombia|Americas
km|Comoros|Africa
cg|Republic of the Congo|Africa
cd|DR Congo|Africa
ck|Cook Islands|Oceania
cr|Costa Rica|Americas
ci|Côte d'Ivoire|Africa
hr|Croatia|Europe
cu|Cuba|Americas
cw|Curaçao|Americas
cy|Cyprus|Europe
cz|Czechia|Europe
dk|Denmark|Europe
dj|Djibouti|Africa
dm|Dominica|Americas
do|Dominican Republic|Americas
ec|Ecuador|Americas
eg|Egypt|Africa
sv|El Salvador|Americas
gq|Equatorial Guinea|Africa
er|Eritrea|Africa
ee|Estonia|Europe
sz|Eswatini|Africa
et|Ethiopia|Africa
fk|Falkland Islands|Americas
fo|Faroe Islands|Europe
fj|Fiji|Oceania
fi|Finland|Europe
fr|France|Europe
gf|French Guiana|Americas
pf|French Polynesia|Oceania
tf|French Southern Territories|Antarctica
ga|Gabon|Africa
gm|Gambia|Africa
ge|Georgia|Asia
de|Germany|Europe
gh|Ghana|Africa
gi|Gibraltar|Europe
gr|Greece|Europe
gl|Greenland|Americas
gd|Grenada|Americas
gp|Guadeloupe|Americas
gu|Guam|Oceania
gt|Guatemala|Americas
gg|Guernsey|Europe
gn|Guinea|Africa
gw|Guinea-Bissau|Africa
gy|Guyana|Americas
ht|Haiti|Americas
hm|Heard Island and McDonald Islands|Antarctica
va|Vatican City|Europe
hn|Honduras|Americas
hk|Hong Kong|Asia
hu|Hungary|Europe
is|Iceland|Europe
in|India|Asia
id|Indonesia|Asia
ir|Iran|Asia
iq|Iraq|Asia
ie|Ireland|Europe
im|Isle of Man|Europe
il|Israel|Asia
it|Italy|Europe
jm|Jamaica|Americas
jp|Japan|Asia
je|Jersey|Europe
jo|Jordan|Asia
kz|Kazakhstan|Asia
ke|Kenya|Africa
ki|Kiribati|Oceania
kp|North Korea|Asia
kr|South Korea|Asia
xk|Kosovo|Europe
kw|Kuwait|Asia
kg|Kyrgyzstan|Asia
la|Laos|Asia
lv|Latvia|Europe
lb|Lebanon|Asia
ls|Lesotho|Africa
lr|Liberia|Africa
ly|Libya|Africa
li|Liechtenstein|Europe
lt|Lithuania|Europe
lu|Luxembourg|Europe
mo|Macau|Asia
mg|Madagascar|Africa
mw|Malawi|Africa
my|Malaysia|Asia
mv|Maldives|Asia
ml|Mali|Africa
mt|Malta|Europe
mh|Marshall Islands|Oceania
mq|Martinique|Americas
mr|Mauritania|Africa
mu|Mauritius|Africa
yt|Mayotte|Africa
mx|Mexico|Americas
fm|Micronesia|Oceania
md|Moldova|Europe
mc|Monaco|Europe
mn|Mongolia|Asia
me|Montenegro|Europe
ms|Montserrat|Americas
ma|Morocco|Africa
mz|Mozambique|Africa
mm|Myanmar|Asia
na|Namibia|Africa
nr|Nauru|Oceania
np|Nepal|Asia
nl|Netherlands|Europe
nc|New Caledonia|Oceania
nz|New Zealand|Oceania
ni|Nicaragua|Americas
ne|Niger|Africa
ng|Nigeria|Africa
nu|Niue|Oceania
nf|Norfolk Island|Oceania
mk|North Macedonia|Europe
mp|Northern Mariana Islands|Oceania
no|Norway|Europe
om|Oman|Asia
pk|Pakistan|Asia
pw|Palau|Oceania
ps|Palestine|Asia
pa|Panama|Americas
pg|Papua New Guinea|Oceania
py|Paraguay|Americas
pe|Peru|Americas
ph|Philippines|Asia
pn|Pitcairn Islands|Oceania
pl|Poland|Europe
pt|Portugal|Europe
pr|Puerto Rico|Americas
qa|Qatar|Asia
re|Réunion|Africa
ro|Romania|Europe
ru|Russia|Europe
rw|Rwanda|Africa
bl|Saint Barthélemy|Americas
sh|Saint Helena|Africa
kn|Saint Kitts and Nevis|Americas
lc|Saint Lucia|Americas
mf|Saint Martin|Americas
pm|Saint Pierre and Miquelon|Americas
vc|Saint Vincent and the Grenadines|Americas
ws|Samoa|Oceania
sm|San Marino|Europe
st|São Tomé and Príncipe|Africa
sa|Saudi Arabia|Asia
sn|Senegal|Africa
rs|Serbia|Europe
sc|Seychelles|Africa
sl|Sierra Leone|Africa
sg|Singapore|Asia
sx|Sint Maarten|Americas
sk|Slovakia|Europe
si|Slovenia|Europe
sb|Solomon Islands|Oceania
so|Somalia|Africa
za|South Africa|Africa
gs|South Georgia and the South Sandwich Islands|Antarctica
ss|South Sudan|Africa
es|Spain|Europe
lk|Sri Lanka|Asia
sd|Sudan|Africa
sr|Suriname|Americas
sj|Svalbard and Jan Mayen|Europe
se|Sweden|Europe
ch|Switzerland|Europe
sy|Syria|Asia
tw|Taiwan|Asia
tj|Tajikistan|Asia
tz|Tanzania|Africa
th|Thailand|Asia
tl|Timor-Leste|Asia
tg|Togo|Africa
tk|Tokelau|Oceania
to|Tonga|Oceania
tt|Trinidad and Tobago|Americas
tn|Tunisia|Africa
tr|Turkey|Asia
tm|Turkmenistan|Asia
tc|Turks and Caicos Islands|Americas
tv|Tuvalu|Oceania
ug|Uganda|Africa
ua|Ukraine|Europe
ae|United Arab Emirates|Asia
gb|United Kingdom|Europe
us|United States|Americas
um|U.S. Minor Outlying Islands|Oceania
uy|Uruguay|Americas
uz|Uzbekistan|Asia
vu|Vanuatu|Oceania
ve|Venezuela|Americas
vn|Vietnam|Asia
vg|British Virgin Islands|Americas
vi|U.S. Virgin Islands|Americas
wf|Wallis and Futuna|Oceania
eh|Western Sahara|Africa
ye|Yemen|Asia
zm|Zambia|Africa
zw|Zimbabwe|Africa
"""

COUNTRIES = {}
for _line in _RAW.strip().splitlines():
    _code, _name, _region = _line.split("|")
    COUNTRIES[_code] = {"code": _code, "name": _name, "region": _region}

# Territories whose flag is identical to another entry make unfair quiz questions.
QUIZ_EXCLUDE = {"bv", "sj", "hm", "um", "mf", "bq", "gf", "gp", "mq", "re", "yt", "pm", "tf"}
QUIZ_CODES = [c for c in COUNTRIES if c not in QUIZ_EXCLUDE]

REGIONS = sorted({c["region"] for c in COUNTRIES.values()})


def flag_url(code, width=320):
    return f"https://flagcdn.com/w{width}/{code}.png"
