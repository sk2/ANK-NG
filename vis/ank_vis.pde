
ArrayList points;
ArrayList edges;

PImage router;
PImage icon_switch;
PImage server;

PFont font;

interface JavaScript {
  void showXYCoordinates(int x, int y);
}

void bindJavascript(JavaScript js) {
  javascript = js;
}

JavaScript javascript;

void mouseClicked() {
  for(int p=0, end=points.size(); p<end; p++) {
    Point pt = (Point) points.get(p);
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
  points = new ArrayList();
  router = loadImage("router.jpg");
  icon_switch = loadImage("switch.jpg");
  server = loadImage("server.jpg");
  font = loadFont("Helvetica.ttf");
  textFont(font, 14);
}

void draw() {
  background(255,255,255);
  for(int p=0, end=points.size(); p<end; p++) {
    Point pt = (Point) points.get(p);
    if(p<end-1) {
      Point next = (Point) points.get(p+1);
      //line(pt.x,pt.y,next.x,next.y);
    }
    pt.draw(); }
}

void clear(){
  points = new ArrayList();
}


Point addPoint(int x, int y, String label, String device_type) {

  icon = router;

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
  points.add(pt);
  return pt;
}

class Point {
  int x,y;
  String label;
  PImage icon;
  Point(int x, int y, String label, PImage icon ) { this.x=x+50; this.y=y+50; this.label = label, this.icon = icon}
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


