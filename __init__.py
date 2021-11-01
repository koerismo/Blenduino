import bpy

board, gpins, hasFirmata = None, [], True

try:
	from pyfirmata import Arduino, PWM
	from serial.serialutil import SerialException
except ImportError:
	hasFirmata = False

class arduinoPanel(bpy.types.Panel):        # panel to display new property
	bl_space_type = "PROPERTIES"        # show up in: object properties
	bl_region_type = "WINDOW"           # show up in: properties panel
	bl_context = "object"               # show up in: the object tab
	bl_label = "Arduino Integration"    # name of the new panel
	
	def draw(self, ctx):
		
		colA = self.layout.column()
		colB = self.layout.column(align=True)

		rowAA = colA.row(align=True)
		rowAA.active = hasFirmata

		rowAAPort = rowAA.column(align=True)
		rowAAPort.active = board == None

		rowAAPort.prop(bpy.context.scene, 'arduino_port', text="")

		if board == None: rowAA.operator('arduino.connect', text='Connect Device')
		else:             rowAA.operator('arduino.disconnect', text='Disconnect Device')

		colA.separator()
		
		rowAB = colA.row()
		rowAB.prop(bpy.context.object, 'arduino_enable', text="Enable Integration", toggle=False )
		
		rowAB.active = board != None
		colB.active = bpy.context.object.arduino_enable and board != None
		
		colB.prop(bpy.context.object, 'arduino_pin_number')
		colB.prop(bpy.context.object, 'arduino_pin_value')


class ConnectArduino(bpy.types.Operator):
	bl_label = "Connect Device"
	bl_description = "Attempt to connect to a device on the specified port"
	bl_idname = "arduino.connect"
	
	def execute( self, context ):
		global board, gpins

		if not hasFirmata:
			self.report({'ERROR'}, 'PyFirmata not loaded! Action aborted.')
			return {'CANCELLED'}

		try:
			board = Arduino( bpy.context.scene.arduino_port )

		except SerialException as err:
			self.report({'ERROR'}, 'An error occurred while attempting to connect to the port: ' + err)
			return {'CANCELLED'}

		gpins = []
		for p in board.digital:
			if p.pin_number < 2: continue
			if p.PWM_CAPABLE: gpins.append( board.get_pin(f'd:{p.pin_number}:p') )
			else:             gpins.append( board.get_pin(f'd:{p.pin_number}:o') )
		
		bpy.app.handlers.frame_change_pre.append(updateAll)
		return {'FINISHED'}
		
class DisconnectArduino(bpy.types.Operator):
	bl_label = "Disconnect Device"
	bl_description = "Disconnect the current device"
	bl_idname = "arduino.disconnect"
	
	def execute( self, context ):
		global board, gpins

		for pin in gpins: pin.write(0)
		gpins = []

		board.exit()
		board = None
		
		bpy.app.handlers.frame_change_pre.remove(updateAll)
		return {'FINISHED'}

def updateAll( frame ):
	if board == None: return
	for obj in bpy.data.objects:
		onChange( obj, None )

def onChange( self, ctx ):
	pinNum = self.arduino_pin_number
	if pinNum-2 < 0 or pinNum-2 >= len(gpins) or not self.arduino_enable or board == None: return
	gpins[pinNum - 2].write( self.arduino_pin_value )

def setEnableState( self, context ):
	pinNum = self.arduino_pin_number
	if pinNum-2 < 0 or pinNum-2 >= len(gpins) or board == None: return
	gpins[pinNum - 2].write( self.arduino_pin_value * self.arduino_enable )

bl_info = {
	"name": "Blenduino",
	"author": "Koerismo",
	"blender": (2, 93, 5),
	"version": (0, 7),
	"description": "A plugin designed for the Arduino Uno. Requires PyFirmata to function!",
	"category": "Object",
}

def register():
	bpy.types.Object.arduino_pin_number = bpy.props.IntProperty(name="Pin Number", description="Arduino pin number", min=2, max=13, default=2)
	bpy.types.Object.arduino_pin_value  = bpy.props.FloatProperty(name="Pin Value" , description="Arduino pin value" , options={'ANIMATABLE'}, min=0, max=1, default=0, update=onChange)
	bpy.types.Object.arduino_enable     = bpy.props.BoolProperty(name="Enable Integration" , description="Enable Arduino integration", default=False, update=setEnableState)
	bpy.types.Scene.arduino_port        = bpy.props.StringProperty(name="Arduino Port", description="The port used to communicate with the Arduino. (e.g. COM5)", default="COM5")
	
	bpy.utils.register_class(arduinoPanel)
	bpy.utils.register_class(ConnectArduino)
	bpy.utils.register_class(DisconnectArduino)

	bpy.app.handlers.frame_change_pre.append(updateAll)
	
def unregister():
	bpy.utils.unregister_class(arduinoPanel)
	bpy.utils.unregister_class(ConnectArduino)
	bpy.utils.unregister_class(DisconnectArduino)

	for pin in gpins: pin.write(0)
	if board != None: board.exit()
	
if __name__ == '__main__': register()
