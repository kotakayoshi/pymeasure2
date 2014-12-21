#! /usr/bin/env python

import time
from ..SCPI import scpi

# main class
# ==========

class E4418(scpi.scpi_family):
    manufacturer = 'Agilent'
    product_name = 'E4418'
    classification = 'Power Meter'
    
    _scpi_enable = '*CLS *DDT *ESE *ESR? *IDN? *OPC *OPT? *RCL *RST *SAV ' +\
                   '*SRE *STB? *TST? *WAI'
    
    def _error_check(self):
        err_num, err_msg = self.error_query()
        error_handler.check(err_num, err_msg)
        return
    
    def error_query(self):
        """
        SYST:ERR? : Query Error Numbers
        -------------------------------
        This query returns error numbers and messages from the power meter's
        error queue. When an error is generated by the power meter, it stores
        an error number and corresponding message in the error queue. One error
        is removed from the error queue each time the SYSTem:ERRor? command is
        executed. The errors are cleared in the order of first-in first-out,
        that is, the oldest errors are cleared first. To clear all the errors
        from the error queue, execute the *CLS command. When the error queue is
        empty, subsequent SYSTem:ERRor? queries return a +0, "No error"
        message. The error queue has a maximum capacity of 30 errors.
        
        Args
        ====
        Nothing.
        
        Returns
        =======
        < err_num : int :  >
            Error number. 0 = 'No Error'
        
        < err_msg : str :  >
            Error message.
        
        Examples
        ========
        >>> p.error_query()
        (0, 'No error.')
        """
        self.com.send('SYST:ERR?')
        ret = self.com.readline()
        ret = ret.strip().split(',')
        err_num = int(ret[0])
        err_msg = ret[1].strip('"')
        return err_num, err_msg
        
    def zeroing(self, ch=1):
        """
        CALn:ZERO:AUTO : Zeroing
        ------------------------
        This command causes the power meter to perform its zeroing routine on
        the specified channel when ONCE is selected. Zeroing takes
        approximately 10 seconds. This adjusts the power meter for a zero power
        reading with no power supplied to the power sensor. The 0|OFF parameter
        is only required for the query response and is ignored in the command.
        If 1|ON is selected, it causes the error -224, "Illegal parameter
        value" to occur.
        
        The command assumes that the power sensor is not connected to a power
        source.
        
        Args
        ====
        < ch : int : 1,2 >
            Specify the channel to perform a zeroing. (1, 2)
            default = 1
        
        Returns
        =======
        Nothing.
        
        Examples
        ========
        p.zeroing()
        p.zeroing(ch=2)
        """
        self.com.send('CAL%d:ZERO:AUTO ONCE'%(ch))
        self._error_check()
        time.sleep(10)
        self._error_check()
        return
        
    
class EPM441A(E4418):
    product_name = 'EPM-4418A'


# ==============
# Helper Classes
# ==============

# Error Class
# ===========
class error_item(object):
    num = 0
    msg = ''
    txt = ''
    
    def __init__(self, num, msg, txt):
        self.num = num
        self.msg = msg
        self.txt = txt
        pass

class error_handler(object):
    error_list = [
        error_item(0, 'No error', ''),
        error_item(-101, 'Invalid character', 'An invalid character was found in the command string. You may have inserted a character such as #, $ or % in the command header or within a parameter. For example, LIM:LOW O#.'),
        error_item(-102, 'Syntax error', 'Invalid syntax was found in the command string. For example, LIM:CLE:AUTO, 1 or LIM:CLE:AUTO 1.'),
        error_item(-103, 'Invalid separator', 'An invalid separator was found in the command string. You may have used a comma instead of a colon, semicolon or blank space; or you may have used a blank space instead of a comma. For example, OUTP:ROSC,1.'),
        error_item(-105, 'GET not allowed', 'A Group Execute Trigger (GET) is not allowed within a command string.'),
        error_item(-108, 'Parameter not allowed', 'More parameters were received than expected for the command. You may have entered an extra parameter or added a parameter to a command that does not accept a parameter. For example, CAL 10.'),
        error_item(-109, 'Missing parameter', 'Fewer parameters were received than expected for the command. You omitted one or more parameters that are required for this command. For example, AVER:COUN.'),
        error_item(-112, 'Program mnemonic too long', 'A command header was received which contained more than the maximum 12 characters allowed. For example, SENSeAVERageCOUNt 8.'),
        error_item(-113, 'Undefined header', 'A command was received that is not valid for this power meter. You may have misspelled the command, it may not be a valid command or you may have the wrong interface selected. If you are using the short form of the command, remember that it may contain up to four letters. For example, TRIG:SOUR IMM.'),
        error_item(-121, 'Invalid character in number', 'An invalid character was found in the number specified for a parameter value. For example, SENS:AVER:COUN 128#H.'),
        error_item(-123, 'Exponent too large', 'A numeric parameter was found whose exponent was larger than 32,000. For example, SENS:COUN 1E34000.'),
        error_item(-124, 'Too many digits', 'A numeric parameter was found whose mantissa contained more than 255 digits, excluding leading zeros.'),
        error_item(-128, 'Numeric data not allowed', 'A numeric value was received within a command which does not accept a numeric value. For example, MEM:CLE 24.'),
        error_item(-131, 'Invalid suffix', 'A suffix was incorrectly specified for a numeric parameter. You may have misspelled the suffix. For example, SENS:FREQ 200KZ.'),
        error_item(-134, 'Suffix too long', 'A suffix used contained more than 12 characters. For example, SENS:FREQ 2MHZZZZZZZZZZZ.'),
        error_item(-138, 'Suffix not allowed', 'A suffix was received following a numeric parameter which does not accept a suffix. For example, INIT:CONT 0Hz.'),
        error_item(-148, 'Character data not allowed', 'A discrete parameter was received but a character string or a numeric parameter was expected. Check the list of parameters to verify that you have used a valid parameter type. For example, MEM:CLE CUSTOM_1.'),
        error_item(-151, 'Invalid string data', 'An invalid string was received. Check to see if you have enclosed the character string in single or double quotes. For example, MEM:CLE "CUSTOM_1.'),
        error_item(-158, 'String data not allowed', 'A character string was received but is not allowed for the command. Check the list of parameters to verify that you have used a valid parameter type. For example, LIM:STAT `ON\'.'),
        error_item(-161, 'Invalid block data', 'A block data element was expected but was invalid for some reason. For example, *DDT #15FET. The 5 in the string indicates that 5 characters should follow, whereas in this example there are only 3.'),
        error_item(-168, 'Block data not allowed', 'A legal block data element was encountered but not allowed by the power meter at this point. For example SYST:LANG #15FETC?.'),
        error_item(-178, 'Expression data not allowed', 'A legal expression data was encountered but not allowed by the power meter at this point. For example SYST:LANG (5+2).'),
        error_item(-211, 'Trigger ignored', 'Indicates that <GET> or *TRG or TRIG:IMM was received and recognized by the device but was ignored because the power meter was not in the wait for trigger state.'),
        error_item(-213, 'Init ignored', 'Indicates that a request for a measurement initiation was ignored as the power meter was already initiated. For example, INIT:CONT ON INIT.'),
        error_item(-214, 'Trigger deadlock', 'TRIG:SOUR was set to HOLD or BUS and a READ? or MEASure? was attempted, expecting TRIG:SOUR to be set to IMMediate.'),
        error_item(-220, 'Parameter error;Frequency list must be in ascending order.', 'Indicates that the frequencies entered using the MEMory:TABLe:FREQuency command are not in ascending order.'),
        error_item(-221, 'Settings conflict', 'This command occurs under a variety of conflicting conditions. The following list gives a few examples of where this error may occur: * If the READ? parameters do not match the current settings. * If you are in fast mode and attempting to switch on for example, averaging, duty cycle or limits. * Trying to clear a sensor calibration table when none is selected.'),
        error_item(-221, 'Settings conflict;DTR/DSR not available on RS422', 'DTR/DSR is only available on the RS232 interface.'),
        error_item(-222, 'Data out of range', 'A numeric parameter value is outside the valid range for the command. For example, SENS:FREQ 2KHZ.'),
        error_item(-224, 'Illegal parameter value', 'A discrete parameter was received which was not a valid choice for the command. You may have used an invalid parameter choice. For example, TRIG:SOUR EXT.'),
        error_item(-226, 'Lists not same length', 'This occurs when SENSe:CORRection:CSET[1]|CSET2:STATe is set to ON and the frequency and calibration/offset lists do not correspond in length.'),
        error_item(-230, 'Data corrupt or stale', 'This occurs when a FETC? is attempted and either a reset has been received or the power meter state has changed such that the current measurement is invalidated (for example, a change of frequency setting or triggering conditions).'),
        error_item(-230, 'Data corrupt or stale;Please zero and calibrate Channel A', 'When CAL[1|2]:RCAL is set to ON and the sensor currently connected to channel A has not been zeroed and calibrated, then any command which would normally return a measurement result (for example FETC?, READ? or MEAS?) will generate this error message.'),
        error_item(-230, 'Data corrupt or stale;Please zero Channel A', 'When CAL[1|2]:RCAL is set to ON and the sensor currently connected to channel A has not been zeroed, then any command which would normally return a measurement result (for example FETC?, READ? or MEAS?) will generate this error message.'),
        error_item(-230, 'Data corrupt or stale;Please calibrate Channel A', 'When CAL[1|2]:RCAL is set to ON and the sensor currently connected to channel A has not been calibrated, then any command which would normally return a measurement result (for example FETC?, READ? or MEAS?) will generate this error message'),
        error_item(-231, 'Data questionable;CAL ERROR', 'Power meter calibration failed. The most likely cause is attempting to calibrate without applying a 1 mW power to the power sensor.'),
        error_item(-231, 'Data questionable;Input Overload', 'The power input to Channel A exceeds the power sensor\'s maximum range.'),
        error_item(-231, 'Data questionable;Lower window log error', 'This indicates that a difference measurement in the lower window has given a negative result when the units of measurement were logarithmic.'),
        error_item(-231, 'Data questionable;Upper window log error', 'This indicates that a difference measurement in the upper window has given a negative result when the units of measurement were logarithmic.'),
        error_item(-231, 'Data questionable;ZERO ERROR', 'Power meter zeroing failed. The most likely cause is attempting to zero when some power signal is being applied to the power sensor.'),
        error_item(-241, 'Hardware missing', 'The power meter is unable to execute the command because either no power sensor is connected or it expects an Agilent E-Series or N8480 Series power sensor, and one is not connected.'),
        error_item(-310, 'System error;Dty Cyc may impair accuracy with ECP sensor', 'This indicates that the sensor connected is for use with CW signals only.'),
        error_item(-310, 'System error;Sensor EEPROM Read Failed - critical data not found or unreadable', 'This indicates a failure with your Agilent E-Series or N8480 Series power sensor. Refer to your power sensor manual for details on returning it for repair.'), 
        error_item(-310, 'System error;Sensor EEPROM Read Completed OK but optional data block(s) not found or unreadable', 'This indicates a failure with your Agilent E-Series or N8480 Series power sensor. Refer to your power sensor manual for details on returning it for repair.'),
        error_item(-310, 'System error;Sensor EEPROM Read Failed - unknown EEPROM table format', 'This indicates a failure with your Agilent E-Series or N8480 Series power sensor. Refer to your power sensor manual for details on returning it for repair.'),
        error_item(-310, 'System error;Sensor EEPROM < > data not found or unreadable', 'Where < > refers to the sensor data block covered, for example, Linearity, Temp - Comp (temperature compensation). This indicates a failure with your Agilent E-Series or N8480 Series power sensor. Refer to your power sensor manual for details on returning it for repair.'),
        error_item(-310, 'System error;Option 001 Battery charger fault', 'The power meter is connected to an AC power source, the battery is not fully charged and it is not charging.'),
        error_item(-310, 'System error;Sensors connected to both front and rear inputs. You cannot connect two power sensors to the one channel input. In this instance, the power', 'meter detects power sensors connected to both its front and rear channel inputs.'),
        error_item(-320, 'Out of memory', 'The power meter required more memory than was available to run an internal operation.'),
        error_item(-330, 'Self-test Failed;', 'The -330, "Self-test Failed" errors indicate that you have a problem with your power meter. Refer to "Contacting Agilent Technologies" on page 103 for details of what to do with your faulty power meter.'),
        error_item(-330, 'Self-test Failed;Measurement Channel Fault', 'Refer to "Measurement Assembly" on page 98 if you require a description of the Measurement Assembly test.'),
        error_item(-330, 'Self-test Failed;Option 001 Battery requires replacement', 'The Option 001 battery is not charging to a satisfactory level and should be replaced.'),
        error_item(-330, 'Self-test Failed;RAM Battery Fault', 'Refer to "RAM Battery" on page 98 if you require a description of the battery test. '),
        error_item(-330, 'Self-test Failed;Calibrator Fault', 'Refer to "Calibrator" on page 99 if you require a description of the calibrator test. '),
        error_item(-330, 'Self-test Failed;ROM Check Failed', 'Refer to "ROM Checksum" on page 98 if you require a description of the ROM Checksum test. '),
        error_item(-330, 'Self-test Failed;RAM Check Failed', 'Refer to "RAM" on page 98 if you require a description of the RAM test. '),
        error_item(-330, 'Self-test Failed;Display Assy. Fault', 'Refer to "Display" on page 99 if you require a description of the Display test. '),
        error_item(-330, 'Self-test Failed;Confidence Check Fault', 'Refer to "Confidence Check" on page 96 if you require a description of this test. '),
        error_item(-330, 'Self-test Failed;Serial Interface Fault', 'Refer to "Serial Interface" on page 99 if you require a description of this test. '),
        error_item(-350, 'Queue overflow', 'The error queue is full and another error has occurred which could not be recorded.'),
        error_item(-361, 'Parity error in program', 'The serial port receiver has detected a parity error and consequently, data integrity cannot be guaranteed.'),
        error_item(-362, 'Framing error in program', 'The serial port receiver has detected a framing error and consequently, data integrity cannot be guaranteed.'),
        error_item(-363, 'Input buffer overrun', 'The serial port receiver has been overrun and consequently, data has been lost.'),
        error_item(-410, 'Query INTERRUPTED', 'A command was received which sends data to the output buffer, but the output buffer contained data from a previous command (the previous data is not overwritten). The output buffer is cleared when power has been off or after *RST (reset) command has been executed.'),
        error_item(-420, 'Query UNTERMINATED', 'The power meter was addressed to talk (that is, to send data over the interface) but a command has not been received which sends data to the output buffer. For example, you may have executed a CONFigure command (which does not generate data) and then attempted to read data from the remote interface.'),
        error_item(-430, 'Query DEADLOCKED', 'A command was received which generates too much data to fit in the output buffer and the input buffer is also full. Command execution continues but data is lost. -440 Query UNTERMINATED after indefinite response The *IDN? command must be the last query command within a command string.'),
    ]
    
    @classmethod
    def check(cls, num, msg):
        if num==0: return
        for e in cls.error_list:
            if msg == e.msg:
                emsg = '%s (%d)'%(e.msg, e.num)
                msg = 'Power meter returned Error message.\n'
                msg += '*'*len(emsg) + '\n'
                msg += emsg + '\n'
                msg += '*'*len(emsg) + '\n'
                msg += e.txt + '\n'
                raise StandardError(msg)
            continue
        _msg = 'Power meter returned Error message.\n'
        emsg = '%s (%d)\n'%(msg, num)
        _msg += '*'*len(emsg) + '\n'
        _msg += emsg
        _msg += '*'*len(emsg) + '\n'
        raise StandardError(_msg)
        return
    
    
