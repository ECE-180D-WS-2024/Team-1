The BLE_Module folder contains all logic regarding BLE functionality.
The BLE_Writer module writes to the BLE_Log.txt file, and then the BLE_Reader module scrapes these values to be used in the Puzzless modules

Code Source:
For the code in this section, we referenced the documentation for common Python libraries such as Numpy, bleak, time, and asyncio.
Additionally, we also referenced various forums such as StackOverflow.

Decisions:
We decided to have the BLE_Writer module write to the BLE_Log.txt file in order to minimize latency.
This is because by doing this, the BLE_Reader module only has to read a txt file of up to 10 lines at a time.

Future Improvements:
In the future, we can probably make further optimizations to decrease the BLE latency.