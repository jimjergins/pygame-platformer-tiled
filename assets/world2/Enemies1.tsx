<?xml version="1.0" encoding="UTF-8"?>
<tileset version="1.10" tiledversion="1.10.2" name="Enemies1" tilewidth="16" tileheight="16" tilecount="294" columns="14">
 <image source="assets/Enemies.png" width="224" height="336"/>
 <tile id="28">
  <properties>
   <property name="availableFrames" value="idle,hit,move"/>
   <property name="hitFrameCount" value="2"/>
   <property name="hitFrameRate" value="3"/>
   <property name="hitFrameStart" value="7"/>
   <property name="idleFrameCount" value="2"/>
   <property name="idleFrameRate" value="10"/>
   <property name="idleFrameStart" value="1"/>
   <property name="moveFrameCount" value="4"/>
   <property name="moveFrameRate" value="3"/>
   <property name="moveFrameStart" value="3"/>
   <property name="velocityX" value="1"/>
  </properties>
  <animation>
   <frame tileid="28" duration="100"/>
   <frame tileid="29" duration="100"/>
   <frame tileid="31" duration="200"/>
   <frame tileid="32" duration="200"/>
   <frame tileid="33" duration="200"/>
   <frame tileid="34" duration="200"/>
   <frame tileid="40" duration="300"/>
   <frame tileid="41" duration="300"/>
  </animation>
 </tile>
</tileset>
