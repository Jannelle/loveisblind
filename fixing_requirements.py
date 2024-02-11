reqs = '''anyio=4.2.0=pyhd8ed1ab_0
bidict=0.22.1=pyhd8ed1ab_0
blinker=1.7.0=pyhd8ed1ab_0
bzip2=1.0.8=h93a5062_5
ca-certificates=2024.2.2=hf0a4a13_0
certifi=2024.2.2=pyhd8ed1ab_0
cffi=1.16.0=py311h4a08483_0
charset-normalizer=3.3.2=pypi_0
click=8.1.3=unix_pyhd8ed1ab_2
cryptography=41.0.7=py311h08c85a6_1
dnspython=2.5.0=pyhd8ed1ab_0
docopt=0.6.2=pypi_0
eventlet=0.33.3=pyhd8ed1ab_0
exceptiongroup=1.2.0=pyhd8ed1ab_2
flask=2.2.3=pyhd8ed1ab_0
flask-socketio=5.3.3=pyhd8ed1ab_0
flask-sqlalchemy=3.0.3=pyhd8ed1ab_0
greenlet=2.0.2=py311ha891d26_1
h11=0.14.0=pyhd8ed1ab_0
h2=4.1.0=pyhd8ed1ab_0
hpack=4.0.0=pyh9f0ad1d_0
httpcore=1.0.2=pyhd8ed1ab_0
hyperframe=6.0.1=pyhd8ed1ab_0
idna=3.6=pyhd8ed1ab_0
importlib-metadata=7.0.1=pyha770c72_0
itsdangerous=2.1.2=pyhd8ed1ab_0
jinja2=3.1.2=pyhd8ed1ab_1
libblas=3.9.0=21_osxarm64_openblas
libcblas=3.9.0=21_osxarm64_openblas
libcxx=16.0.6=h4653b0c_0
libexpat=2.5.0=hb7217d7_1
libffi=3.4.2=h3422bc3_5
libgfortran=5.0.0=13_2_0_hd922786_3
libgfortran5=13.2.0=hf226fd6_3
liblapack=3.9.0=21_osxarm64_openblas
libopenblas=0.3.26=openmp_h6c19121_0
libsqlite=3.45.1=h091b4b1_0
libzlib=1.2.13=h53f4e23_5
llvm-openmp=17.0.6=hcd81f8e_0
markupsafe=2.1.2=py311he2be06e_0
ncurses=6.4=h463b476_2
numpy=1.26.3=py311h7125741_0
openssl=3.2.1=h0d3ecfb_0
pandas=2.2.0=py311hfbe21a1_0
pip=23.3.2=pyhd8ed1ab_0
pycparser=2.21=pyhd8ed1ab_0
pyopenssl=24.0.0=pyhd8ed1ab_0
python=3.11.7=hdf0ec26_1_cpython
python-dateutil=2.8.2=pyhd8ed1ab_0
python-engineio=4.4.0=pyhd8ed1ab_0
python-socketio=5.8.0=pyhd8ed1ab_0
python-tzdata=2023.4=pyhd8ed1ab_0
python_abi=3.11=4_cp311
pytz=2023.4=pyhd8ed1ab_0
readline=8.2=h92ec313_1
requests=2.31.0=pypi_0
setuptools=69.0.3=pyhd8ed1ab_0
six=1.16.0=pyh6c4a22f_0
sniffio=1.3.0=pyhd8ed1ab_0
sqlalchemy=2.0.25=py311h05b510d_0
tk=8.6.13=h5083fa2_1
typing-extensions=4.9.0=hd8ed1ab_0
typing_extensions=4.9.0=pyha770c72_0
tzdata=2024a=h0c530f3_0
urllib3=2.2.0=pypi_0
werkzeug=2.2.3=pyhd8ed1ab_0
wheel=0.42.0=pyhd8ed1ab_0
xz=5.2.6=h57fd34a_0
yarg=0.1.9=pypi_0
zipp=3.17.0=pyhd8ed1ab_0'''

for req in reqs.split('\n'):
    print("=".join(req.split('=')[:2]))