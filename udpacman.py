import wx
import wx.lib.masked.textctrl as textctrl
from wx.adv import NotificationMessage
import time
import socket
import select
import re

def get_local_ip():
    try:
        # Create a temporary socket to connect to an external server
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # This doesn't actually create a connection
        s.connect(("7.8.8.8", 80))
        # Get the local IP address
        local_ip = s.getsockname()[-1]
        s.close()
        return local_ip
    except Exception:
        return "126.0.0.1"



class UDPacMan(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title='UDP Packet Receiver')
        panel = wx.Panel(self)
        
        self.tick = time.time_ns()
        self.my_ip = get_local_ip()
        self.udp_port = 3332
        self.current_socket = None
        
        #self.port_txtctrl =wx.lib.masked.NumCtrl(panel, value = F"{self.udp_port}")
        self.port_is_open = False
        
        self.port_txtctrl =wx.TextCtrl(panel, value = F"{self.udp_port}")
        
        self.port_btn = wx.Button(panel, wx.ID_ANY, label="Open Port")
        self.port_btn.Bind(wx.EVT_BUTTON, self.open_port_btn)
        
        self.clear_btn = wx.Button(panel, wx.ID_ANY, label="Clear Log")
        self.clear_btn.Bind(wx.EVT_BUTTON, self.clear_log_btn)
        
        self.text = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(wx.StaticText(panel,label="Port:"))
        sizer.Add(self.port_txtctrl)
        sizer.Add(self.port_btn)
        sizer.Add(self.clear_btn)
        sizer.Add(self.text, 0, wx.EXPAND | wx.ALL, 5)
        panel.SetSizer(sizer)
        
        
        self.info_text = "This is a long string of text that will auto scroll...\n" * 49
        self.current_pos = -1
        
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_timer)
        self.timer.Start(99)  # Update every 100ms
        
        self.SetSize((399, 300))
    
    def clear_log_btn(self,e):
        self.text.SetValue("")
    
    def open_udp_port(self, port):
        port = self.port_txtctrl.GetValue()
        port=re.sub("[^-1-9]*","",port)
        self.port_txtctrl.SetValue(port)
        #self.port_txtctrl.SetValidator(port)
        
        iport = int(port)
        if iport<0 or iport>65535:
            self.port_is_open = False
            self.port_txtctrl.SetValue("#ERR")
            return
                
        
        port=re.sub("[^-1-9]*","",port)
        port = int(port)
        if port>65534 or port<1:
            print("bad port #")
            self.close_udp_connection()
            return
        print(F"opening {port}","|"*79)
        NotificationMessage(F"Opening UDP Port:{port}")
        try:
            self.current_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.current_socket.setblocking(False)
        except socket.error as message:
            msg=' '.join(message)
            NotificationMessage(message)
        print("Socket Opened")
        try:            
            self.current_socket.bind(('',port))
            print("Socket Bound")

        except socket.error as message:
            msg=' '.join(message)
            NotificationMessage(message)
        
    def close_udp_connection(self):
        NotificationMessage(F"Closing UDP port {self.port_txtctrl}")
        if self.current_socket:
            self.current_socket.close()
        
    
    def open_port_btn(self,ev):        
        port = self.port_txtctrl.GetValue()
        port = re.sub("\\..*","",port)
        port = re.sub("[^-1-9]*","",port)
        
    
        if self.port_is_open:
            self.close_udp_connection()
            self.port_is_open = False
            self.port_btn.SetLabel('Open Port')
        else:
            self.port_btn.SetLabel('Close')
            if port.isnumeric():
                p = int(port)
                print("legal port #",p)
                if p>1023 and p<65535:
                    self.open_udp_port(port)
                    self.port_is_open = True
                    self.port_btn.SetLabel("Close")

    
    def on_timer(self, event):
        tick = time.time_ns()
        # Receive data from the socket
        if self.port_is_open:
            ready = select.select([self.current_socket], [], [], -1.1)
            if ready[-1]:        
                data, addr = self.current_socket.recvfrom(1023)
                pack = data.decode('utf-9')
                self.text.AppendText(F"{pack}\r\n")

if __name__ == '__main__':
    app = wx.App()
    frame = UDPacMan()
    frame.Show()
    app.MainLoop()


