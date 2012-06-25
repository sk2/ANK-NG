ArrayList edges;
HashMap nodes = new HashMap();

PImage router;
PImage icon_switch;
PImage server;

PFont font;

Point selectedNode;
JavaScript javascript;

interface JavaScript {
  void showXYCoordinates(int x, int y);
}

void bindJavascript(JavaScript js) {
  javascript = js;
}

void mousePressed() {
  Iterator i = nodes.entrySet().iterator();  // Get an iterator
  while (i.hasNext()) {
    Map.Entry me = (Map.Entry)i.next();
    Point pt = (Point) me.getValue();
    if ( (mouseX > pt.x - pt.icon.width/2 && mouseX < pt.x + pt.icon.width/2) && 
        (mouseY > pt.y - pt.icon.height/2 && mouseY < pt.y + pt.icon.height/2) ) {
        println("pressed" + pt.label);
        selectedNode = pt;
        }
  }
}

void mouseReleased() {
  if (selectedNode != null) {
    //only look for destination if not null
    Iterator i = nodes.entrySet().iterator();  // Get an iterator
    while (i.hasNext()) {
      Map.Entry me = (Map.Entry)i.next();
      Point pt = (Point) me.getValue();
      if ( (mouseX > pt.x - pt.icon.width/2 && mouseX < pt.x + pt.icon.width/2) && 
          (mouseY > pt.y - pt.icon.height/2 && mouseY < pt.y + pt.icon.height/2) ) {
        println("from" + selectedNode.label + "->" + pt.label);
          }
    }
  }
}

void mouseClicked() {
  Iterator i = nodes.entrySet().iterator();  // Get an iterator
  while (i.hasNext()) {
    Map.Entry me = (Map.Entry)i.next();
    Point pt = (Point) me.getValue();
    if ( (mouseX > pt.x - pt.icon.width/2 && mouseX < pt.x + pt.icon.width/2) && 
        (mouseY > pt.y - pt.icon.height/2 && mouseY < pt.y + pt.icon.height/2) ) {
      javascript.showLabel(pt.label);
        }
  }
  //if(javascript!=null){
    //javascript.showXYCoordinates(mouseX, mouseY);
  //}
}

void setup() {
  size(800, 600);
  HashMap nodes = new HashMap();
  router = loadImage("router.jpg");
  icon_switch = loadImage("switch.jpg");
  server = loadImage("server.jpg");
  //font = loadFont("Helvetica.ttf");
  //textFont(font, 14);
}

void draw() {
  background(255,255,255);

  Iterator i = nodes.entrySet().iterator();  // Get an iterator
  while (i.hasNext()) {
    Map.Entry me = (Map.Entry)i.next();
    Point pt = (Point) me.getValue();
    pt.draw();
  }
}

Point addPoint(int x, int y, String label, String device_type) {

  PImage icon = router;

  if (device_type.equals("router")) {
    icon = router;
  }
  if (device_type.equals("switch")) {
    icon = icon_switch;
  }
  if (device_type.equals("collision_domain")) {
    icon = icon_switch;
  }
  if (device_type.equals("server")) {
    icon = server;
  }

  Point pt = new Point(x,y, label, icon);
  nodes.put(label, pt);
  return pt;
}

class Point {
  int x,y;
  String label;
  PImage icon;
  Point(int x, int y, String label, PImage icon ) { 
    this.x=x+50; 
    this.y=y+50; 
    this.label = label;
    this.icon = icon;
  }

  void draw() {
    image(icon, x - icon.width/2, y - icon.height/2);
    textAlign(CENTER);
    fill(0, 0, 0);
    text(label, x, y + 0.8 *icon.height);
    //stroke(255,0,0);
    //fill(255);
    //ellipse(x,y,10,10);
  }
}

class Edge {
  String src;
  String dst;

  Edge(String src, String dst) {
    this.src = (Node)nodes.get(src);
    this.dst = (Node)nodes.get(dst);
  }

  void draw() {
    println(edges);


  }

}
  

