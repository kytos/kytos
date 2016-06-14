# Kytos - kyco

[![Openflow][of-icon]][of-url]
[![Tag][tag-icon]][tag-url]
[![Release][release-icon]][release-url]
[![Tests][tests-icon]][tests-url]
[![License][license-icon]][license-url]

*Kyco* is the main component of Kytos Project. Kytos Controller (Kyco) uses
*python-openflow* library to parse low level OpenFlow messages.

This code is part of *Kytos* project and was developed to be used with *Kytos*
controller.

For more information about, please visit our [Kytos web site][kytos-url].

## Installing


## Usage


## Main Highlights

### Speed focused

We keep the word *performance* in mind since the beginning of the development.
Also, as computer scientists, we will always try to get the best performance by
using the most suitable algorithms.

Some of our developers participated in several demonstrations involving tests
with high-speed networks (~1 terabit/s), some even involving data transfers
from/to CERN.

### Always updated

To avoid code repetition this project utilizes an incremental architecture.

This means that the first version (1.0.0 = v0x01) was coded from the full
OpenFlow 1.0.2 Protocol. The 1.1 version (v0x02) imports the 1.0 version and
then do the necessary changes to make it compatible with the OpenFlow 1.1.0
Protocol, and the next version follows the same logic.

Using incremental code makes the implementation of new versions of OpenFlow
protocol faster. Our main goal is to follow the specifications since the very
beginning.

### Easy to learn

Python is an easy language to learn and we aim at writing code in a "pythonic
way". We also provide a well documented API. Thus, learning to make your
controller using this library is a trivial task.

### Born to be free

OpenFlow was born with a simple idea: make your network more vendor agnostic
and we like that!

We are advocates and supporters of free software and we believe that the more
eyes observe the code, the better it will be. This project can receive support
from many vendors, but will never follow a particular vendor direction.

*python-openflow* will always be free software.

## Authors

This is a collaborative project between SPRACE (From São Paulo State University,
Unesp) and Caltech (California Institute of Technology). For a complete list of
authors, please open `AUTHORS.md` file.

## Contributing

If you want to contribute to this project, please read
[CONTRIBUTE.md](CONTRIBUTE.md) and [HACKING.md](HACKING.md) files.

## License

This software is under _MIT-License_. For more information please read `LICENSE`
file.

[api-reference-url]: http://docs.kytos.io/python-openflow/api-reference/
[kytos-url]: http://kytos.io/
[of-icon]: https://img.shields.io/badge/Openflow-1.0.0-brightgreen.svg
[of-url]: https://www.opennetworking.org/images/stories/downloads/sdn-resources/onf-specifications/openflow/openflow-spec-v1.0.0.pdf
[tag-icon]: https://img.shields.io/github/tag/kytos/python-openflow.svg
[tag-url]: https://github.com/kytos/python-openflow/tags
[release-icon]: https://img.shields.io/github/release/kytos/python-openvpn.svg
[release-url]: https://github.com/kytos/python-openflow/releases
[tests-icon]: http://kytos.io/imgs/tests-status.svg
[tests-url]: https://github.com/kytos/python-openflow
[license-icon]: https://img.shields.io/github/license/kytos/python-openflow.svg
[license-url]: https://github.com/kytos/python-openflow/blob/master/LICENSE
