include <cutbox.scad>

panel_size  = 128;  // mm
max_height  = 142;  // mm
thickness   = 6.35; // mm => 1/4 inch

margin = (max_height - panel_size) / 2;

width = 3 * panel_size + 2* margin;
height = panel_size + 2* margin;
depth = 180;
spacing = 5;



box(width = width, height = height, depth = depth, thickness = thickness, assemble = false,spacing=spacing, holes = [[0,5], [15,5]], hole_dia=5, margin = margin, panel_size=panel_size);

translate([(width+spacing)*2.5, height*1.5 + spacing])
  difference(){
    square([width,height],true);
    square([width-2*margin,height-2*margin],true);
  }
total_width = (width+spacing)*2.5 + width/2;
total_height = height+spacing+ depth;
  
echo("total_width");
echo(total_width);
echo("total_height");
echo(total_height);