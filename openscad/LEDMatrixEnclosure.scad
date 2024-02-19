include <cutbox.scad>

panel_size  = 128;  // mm
max_height  = 142;  // mm
//thickness   = 6.35; // mm => 1/4 inch
//thickness   = 3.175; // mm => 0.125x inch
thickness   = 3; // mm ACM 3 mm
tolerence_frame=0.5;

margin = (max_height - panel_size) / 2;

width = 3 * panel_size + 2* margin;
height = panel_size + 2* margin;
depth = 180;
spacing = 4.5;
airgap_width = 0;
kerf=-0.15;
finger_cutout_radius=0;
finger_cutout_offset=0;

box(width = width, height = height, depth = depth, thickness = thickness
,finger_width=2*6.35, finger_margin=2*6.35,  assemble = false,spacing=spacing, holes = [],airgap_width=airgap_width, hole_dia=5,finger_cutout_radius= finger_cutout_radius, finger_cutout_offset=finger_cutout_offset,kerf=kerf,margin = margin, panel_size=panel_size);

translate([(width+spacing)*2.5, height*1.5 + spacing])
  difference(){
    square([width,height],true);
    square([width-2*margin + tolerence_frame,height-2*margin + tolerence_frame],true);
  }
translate([margin + 4.8 * width/2 , margin +3 * height /2 ]) square([0.695*width, 0.695 * height], true);
translate([ 5.7 * width/2 , margin +3 * height /2 ]) square([30, 60], true);
translate([ 5.9 * width/2 , margin +3 * height /2 ]) square([30, 60], true);
  
  
total_width = (width+spacing)*2.5 + width/2;
total_height = height+spacing+ depth;
  
echo("total_width");
echo(total_width);
echo("total_height");
echo(total_height);