# PyMDO

Tektronix MDO3 series oscilloscope control in Python

## Introduction

There are two classes provided - `SyncMDO3` and `AsyncMDO3`.
The `SyncMDO3` is Synchronous, while the `AsyncMDO3` is asynchronous.
The former is easier to use; however, it is relatively slow compared to the latter. 
Also, in complex situations, 
the asynchronous version is more suitable as it is possible to control 
many instruments concurrently using Python's `async` and `await` paradigms.

## Usage - Synchronous

First, instantiate the oscilloscope class.

```python
m = SyncMDO3(ipaddress: str, portnumber: int)
```

`ipaddress` is the IP address of the oscilloscope, while port number is the Socket server port number.
For example, if the scope has an IP address 10.33.20.166 at port 4000, 
instantiation is done by `m = SyncMDO3("10.33.20.166", 5000)`.

To send commands to the oscilloscope, there are two methods - `write` and `query`.
The `write` method just writes the command without waiting for the reply from the oscilloscope.
The `query` method writes the command to the scope and waits for it to send a response.
Use these methods carefully. The oscilloscope does not send any response to many commands.
If `query` method is used to send such commands, the call will block as the method waits for the response.
As a rule of thumb, use `query` method when the command ends in a question mark (?); otherwise, use `write`.
For example `query` method is required for `*idn?`.

```python
m.write(command: str) # Write a command
m.query(command: str) -> str # Write a command and then wait for response
```
For example, to query the identity of the instrument, `idn = m.query("*idn?")`
