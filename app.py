{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 18,
   "metadata": {},
   "outputs": [],
   "source": [
    "from matplotlib import style\n",
    "style.use('fivethirtyeight')\n",
    "import matplotlib.pyplot as plt\n",
    "\n",
    "import numpy as np\n",
    "import pandas as pd\n",
    "import datetime as dt\n",
    "\n",
    "import sqlalchemy\n",
    "from sqlalchemy.ext.automap import automap_base\n",
    "from sqlalchemy.orm import Session\n",
    "from sqlalchemy import create_engine, func, inspect\n",
    "\n",
    "from flask import Flask, jsonify\n",
    "\n",
    "engine = create_engine(\"sqlite:///Resources/hawaii.sqlite\")\n",
    "\n",
    "# reflect an existing database into a new model\n",
    "Base = automap_base()\n",
    "# reflect the tables\n",
    "Base.prepare(engine, reflect=True)\n",
    "\n",
    "# Save reference to the table\n",
    "Measurement = Base.classes.measurement\n",
    "Station = Base.classes.station\n",
    "\n",
    "# Create our session (link) from Python to the DB\n",
    "session = Session(engine)\n",
    "\n",
    "app = Flask(__name__)\n",
    "\n",
    "\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 19,
   "metadata": {},
   "outputs": [],
   "source": [
    "@app.route(\"/\")\n",
    "def welcome():\n",
    "    \"\"\"List all available api routes.\"\"\"\n",
    "    return (\n",
    "        f\"Available Routes:<br/>\"\n",
    "        f\"/api/v1.0/precipitation<br/>\"\n",
    "        f\"/api/v1.0/stations<br/>\"\n",
    "        f\"/api/v1.0/tobs<br/>\"\n",
    "        f\"/api/v1.0/<start><br/>\"\n",
    "        f\"/api/v1.0/<start>/<end><br/>\"\n",
    "    )\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 20,
   "metadata": {},
   "outputs": [],
   "source": [
    "@app.route(\"/api/v1.0/precipitation\")\n",
    "def precipitation():\n",
    "    last_data_point = session.query(Measurement.date).order_by(Measurement.date.desc()).first()\n",
    "    year_ago = dt.date(2017,8,23) - dt.timedelta(days= 365)\n",
    "\n",
    "    year_prcp = session.query(Measurement.date, Measurement.prcp).\\\n",
    "    filter(Measurement.date >= year_ago, Measurement.prcp != None).\\\n",
    "    order_by(Measurement.date).all()\n",
    "    return jsonify(dict(year_prcp))"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 21,
   "metadata": {},
   "outputs": [],
   "source": [
    "@app.route(\"/api/v1.0/tobs\")\n",
    "def tobs():\n",
    "    \n",
    "    year_ago = dt.date(2017,8,23) - dt.timedelta(days= 365)\n",
    "    year_temp = session.query(Measurement.tobs).\\\n",
    "        filter(Measurement.date >= year_ago, Measurement.station == 'USC00519281').\\\n",
    "         order_by(Measurement.tobs).all()\n",
    "\n",
    "    yr_temp = []\n",
    "    for y_t in year_temp:\n",
    "        yrtemp = {}\n",
    "        yrtemp[\"tobs\"] = y_t.tobs\n",
    "        yr_temp.append(yrtemp)\n",
    "\n",
    "    return jsonify(yr_temp)\n",
    "\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 22,
   "metadata": {},
   "outputs": [],
   "source": [
    "def calc_start_temps(start_date):\n",
    "    \"\"\"TMIN, TAVG, and TMAX for a list of dates.\n",
    "    \n",
    "    Args:\n",
    "        start_date (string): A date string in the format %Y-%m-%d\n",
    "        end_date (string): A date string in the format %Y-%m-%d\n",
    "        \n",
    "    Returns:\n",
    "        TMIN, TAVE, and TMAX\n",
    "    \"\"\"\n",
    "    \n",
    "    return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\\\n",
    "        filter(Measurement.date >= start_date).all()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 23,
   "metadata": {},
   "outputs": [],
   "source": [
    "@app.route(\"/api/v1.0/<start>\")\n",
    "    \n",
    "def start_date(start):\n",
    "    calc_start_temp = calc_start_temps(start)\n",
    "    t_temp= list(np.ravel(calc_start_temp))\n",
    "\n",
    "    t_min = t_temp[0]\n",
    "    t_max = t_temp[2]\n",
    "    t_avg = t_temp[1]\n",
    "    t_dict = {'Minimum temperature': t_min, 'Maximum temperature': t_max, 'Avg temperature': t_avg}\n",
    "\n",
    "    return jsonify(t_dict)\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 24,
   "metadata": {},
   "outputs": [],
   "source": [
    "def calc_temps(start_date, end_date):\n",
    "    \"\"\"TMIN, TAVG, and TMAX for a list of dates.\n",
    "    Args:\n",
    "    start_date (string): A date string in the format %Y-%m-%d\n",
    "    end_date (string): A date string in the format %Y-%m-%d\n",
    "    Returns:\n",
    "    TMIN, TAVE, and TMAX\n",
    "    \"\"\"\n",
    "    return session.query(func.min(Measurement.tobs), \\\n",
    "                         func.avg(Measurement.tobs), \\\n",
    "                         func.max(Measurement.tobs)).\\\n",
    "                         filter(Measurement.date >= start_date).\\\n",
    "                         filter(Measurement.date <= end_date).all()\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 25,
   "metadata": {},
   "outputs": [],
   "source": [
    "@app.route(\"/api/v1.0/<start>/<end>\")\n",
    "\n",
    "def start_end_date(start, end):\n",
    "    \n",
    "    calc_temp = calc_temps(start, end)\n",
    "    ta_temp= list(np.ravel(calc_temp))\n",
    "\n",
    "    tmin = ta_temp[0]\n",
    "    tmax = ta_temp[2]\n",
    "    temp_avg = ta_temp[1]\n",
    "    temp_dict = { 'Minimum temperature': tmin, 'Maximum temperature': tmax, 'Avg temperature': temp_avg}\n",
    "\n",
    "    return jsonify(temp_dict)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 26,
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      " * Serving Flask app \"__main__\" (lazy loading)\n",
      " * Environment: production\n",
      "   WARNING: This is a development server. Do not use it in a production deployment.\n",
      "   Use a production WSGI server instead.\n",
      " * Debug mode: on\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      " * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)\n",
      " * Restarting with fsevents reloader\n"
     ]
    },
    {
     "ename": "SystemExit",
     "evalue": "1",
     "output_type": "error",
     "traceback": [
      "An exception has occurred, use %tb to see the full traceback.\n",
      "\u001b[0;31mSystemExit\u001b[0m\u001b[0;31m:\u001b[0m 1\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "/Users/gagethompson/opt/anaconda3/lib/python3.7/site-packages/IPython/core/interactiveshell.py:3339: UserWarning: To exit: use 'exit', 'quit', or Ctrl-D.\n",
      "  warn(\"To exit: use 'exit', 'quit', or Ctrl-D.\", stacklevel=1)\n"
     ]
    }
   ],
   "source": [
    "if __name__ == '__main__':\n",
    "    app.run(debug=True)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.7.6"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 4
}
