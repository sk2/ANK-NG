
ArrayList points;

PImage router;


 
   void setup() {
     size(800, 600);
     points = new ArrayList();
     b = loadImage("router.jpg");
   }
 
   void draw() {
     background(255,255,255);
     for(int p=0, end=points.size(); p<end; p++) {
       Point pt = (Point) points.get(p);
       if(p<end-1) {
         Point next = (Point) points.get(p+1);
         line(pt.x,pt.y,next.x,next.y); }
       pt.draw(); }
   }

  void clear(){
    points = new ArrayList();
  }
 
   void mouseClicked() {
     //addPoint(mouseX,mouseY);
   }
 
   Point addPoint(int x, int y) {
     Point pt = new Point(x,y);
     points.add(pt);
     return pt;
   }
 
   class Point {
     int x,y;
     Point(int x, int y) { this.x=x+50; this.y=y+50; }
     void draw() {
       image(b, x - b.width/2, y - b.height/2);
       //stroke(255,0,0);
       //fill(255);
       //ellipse(x,y,10,10);
     }
   }
