#define USE_HOLDING_REGISTERS_ONLY
#include <ESP8266WiFi.h>
#include <Modbus.h>
#include <ModbusIP_ESP8266.h>

//////////////// registers of DNA_CASE ///////////////////
enum
{
  // The first register starts at address 0
  ACTIONS,      // Always present, used for incoming actions

  // Any registered events, denoted by 'triggered_by_register' in rs485_node of Lua script, 1 and up
  DELIVER_DNA,
  
  TOTAL_ERRORS,     // leave this one, error counter
  TOTAL_REGS_SIZE   // INTERNAL: total number of registers for function 3 and 16 share the same register array
};

//ModbusIP object
ModbusIP mb;

// Action handler. Add all your actions mapped by action_id in rs485_node of Lua script
void process_actions() {
  if (mb.Hreg(ACTIONS) == 0)
    return;

  switch (mb.Hreg(ACTIONS)) {
    case 1 : // Put here code for Reset
      Serial.println("[Reset] action fired");
      // gpioWrite(1, LED_BUILTIN);
      break;
    }

  // Signal that action was processed
  mb.Hreg(ACTIONS, 0);
}

// Just debug functions for easy testing. Won't be used probably
/* Holds current button state in register */
void buttonStatus(int reg, int pin) { // LOOP
  mb.Hreg(reg, pin);
}
void buttonStatus_setup(int reg, int pin) { // SETUP
  pinMode(pin, INPUT_PULLUP);
}

/* Outputs register value to pin */
void gpioWrite(int reg, int pin) {
  digitalWrite(pin, mb.Hreg(reg));
}
/////////////////////////////////////////////////////////////////

void setup()
{
  Serial.begin(115200);
  Serial.println("TCP ModBus Slave DNA_CASE:192.168.118.56 for lua/Aliens.lua");

  mb.config("MT29501119", "ENTER_WIFI_PASS");
  WiFi.config(IPAddress(192, 168, 118, 56), IPAddress(), IPAddress(), IPAddress(), IPAddress());

  Serial.print("Connecting to MT29501119 ");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
 
  Serial.println(" CONNECTED!");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());

  Serial.print("Netmask: ");
  Serial.println(WiFi.subnetMask());

  Serial.print("Gateway: ");
  Serial.println(WiFi.gatewayIP());

  mb.addHreg(ACTIONS, 0);
  mb.addHreg(DELIVER_DNA, 0);
  // Sample calls
  // buttonStatus_setup(DELIVER_DNA, <buttonPin>);
}


void loop()
{
  mb.task();              // not implemented yet: mb.Hreg(TOTAL_ERRORS, mb.task());
  process_actions();

  // Notify main console of local events
  // mb.Hreg(DELIVER_DNA, 1);
  

  // Sample calls
  // buttonStatus(DELIVER_DNA, <buttonPin>);
}